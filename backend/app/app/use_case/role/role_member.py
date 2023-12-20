from typing import List
from sqlalchemy import select, func

from app.db.orm_types import GreenPlumSession
from . import MemberDTO, RoleGroupDTO, RoleGroupEdgeDTO, RoleGroupNodeDTO
from app.core.config import settings
from app.read_model import *

_pg_get_userbyid = func.pg_catalog.pg_get_userbyid

_pg_role_links = (
    select([
        pg_auth_members.c.roleid.label('from_oid'),
        pg_auth_members.c.member.label('to_oid'),
    ])
    .select_from(
        pg_auth_members
    )
)


_pg_role_members = (
    select([
        pg_auth_members.c.member.label('oid'),
        _pg_get_userbyid(pg_auth_members.c.member).label('rolname'),
    ])
    .select_from(
        pg_auth_members
    )
)

_pg_role_stmt = (
    select([
        pg_roles.c.oid,
        pg_roles.c.rolname,
    ])
    .select_from(
        pg_roles
    )
)


def _revoke_member_from_role(
    conn: GreenPlumSession, rolname: str, member: str, admin_option: bool = False
) -> None:
    '''
    REVOKE [ ADMIN OPTION FOR ]
        role_name [, ...] FROM role_name [, ...]
        [ CASCADE | RESTRICT ]
    '''

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'REVOKE %s "%s" FROM "%s" CASCADE',
                :admin_option, :rolname, :member);
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "admin_option": 'ADMIN OPTION FOR' if admin_option else '',
            "rolname": rolname,
            "member": member,
        },
    )


def _grant_member_to_role(
    conn: GreenPlumSession, rolname: str, member: str, admin_option: bool = False
) -> None:
    '''
    GRANT role_name [, ...] TO role_specification [, ...]
    [ WITH ADMIN OPTION ]
    [ GRANTED BY role_specification ]
    '''

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'GRANT "%s" TO "%s" %s',
                :rolname, :member, :admin_option);
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "rolname": rolname,
            "member": member,
            "admin_option": 'WITH ADMIN OPTION' if admin_option else '',
        },
    )


def get_role_members(conn: GreenPlumSession, dbuser: str) -> List[MemberDTO]:
    stmt = _pg_role_members.where(_pg_get_userbyid(pg_auth_members.c.roleid) == dbuser)
    with conn.begin():
        rows = conn.execute(stmt)
        return [MemberDTO(**row) for row in rows]


def get_graph_of_members(conn: GreenPlumSession) -> RoleGroupDTO:
    with conn.begin():
        nodes = conn.execute(_pg_role_stmt)
        edges = conn.execute(_pg_role_links)

        return RoleGroupDTO(
            nodes=[RoleGroupNodeDTO(**row) for row in nodes],
            edges=[RoleGroupEdgeDTO(**row) for row in edges]
        )


def remove_member_from_role(conn: GreenPlumSession, dbuser: str, member: str) -> None:
    with conn.begin():
        _revoke_member_from_role(conn, dbuser, member)


def append_member_to_role(conn: GreenPlumSession, dbuser: str, member: str) -> None:
    with conn.begin():
        _grant_member_to_role(
            conn=conn,
            rolname=dbuser,
            member=member,
            admin_option=settings.GRANT_WITH_ADMIN_OPTION
        )

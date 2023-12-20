from typing import Iterator, List, Optional
from sqlalchemy import exc

from app.core.config import settings
from app.use_case.exceptions import DoneWithErrors
from app.db.orm_types import GreenPlumSession
from . import GrantDatabaseDTO, GrantDatabasePrivelegesDTO
from app.read_model import *
from app.use_case.acl import get_database_acl
from app.use_case.privilege import parce_acl_rules


def _calc_grant_options(privileges: GrantDatabasePrivelegesDTO) -> List[str]:
    grant_options = {
        'CREATE': privileges.create,
        'CONNECT': privileges.connect,
        'TEMPORARY': privileges.temporary,
    }

    return list(
        map(
            lambda item: item[0],
            filter(lambda item: item[1], grant_options.items())
        )
    )


def _calc_revoke_options(privileges: GrantDatabasePrivelegesDTO, *, all: bool = False) -> List[str]:
    revoke_options = {
        'CREATE': privileges.create,
        'CONNECT': privileges.connect,
        'TEMPORARY': privileges.temporary,
    }

    if all:
        return revoke_options.keys()

    return list(
        map(
            lambda item: item[0],
            filter(lambda item: not item[1], revoke_options.items())
        )
    )


def _grant_database_permissions(conn: GreenPlumSession, payload: GrantDatabaseDTO) -> None:
    '''
    GRANT { { CREATE | CONNECT | TEMPORARY | TEMP } [, ...] | ALL [ PRIVILEGES ] }
        ON DATABASE database_name [, ...]
        TO role_specification [, ...] [ WITH GRANT OPTION ]
    '''

    grant_options = _calc_grant_options(payload.privileges)

    if not grant_options:
        return

    sql_command = """
        DO $$ BEGIN
            SET ROLE NONE;
            EXECUTE FORMAT(
                'GRANT %s ON DATABASE "%s" TO "%s" %s',
                :grant_options, :database_name, :role_specification, :with_grant_option
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grant_options": ', '.join(grant_options),
            "database_name": payload.name,
            "role_specification": payload.role_specification,
            "with_grant_option": 'WITH GRANT OPTION' if payload.with_grant_option else '',
        }
    )


def _revoke_database_permissions(conn: GreenPlumSession, payload: GrantDatabaseDTO, grantor: Optional[str] = None) -> None:
    '''
    REVOKE [ GRANT OPTION FOR ]
        { { CREATE | CONNECT | TEMPORARY | TEMP } [, ...] | ALL [ PRIVILEGES ] }
        ON DATABASE database_name [, ...]
        FROM { [ GROUP ] role_name | PUBLIC } [, ...]
        [ CASCADE | RESTRICT ]
    '''

    revoke_options = _calc_revoke_options(payload.privileges, all=True)

    if not revoke_options:
        return

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT('SET ROLE %s', :grantor);
            EXECUTE FORMAT(
                'REVOKE %s ON DATABASE "%s" FROM "%s" CASCADE',
                :revoke_options, :database_name, :role_specification
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grantor": f'"{grantor}"' if grantor else 'NONE',
            "revoke_options": ', '.join(revoke_options),
            "database_name": payload.name,
            "role_specification": payload.role_specification,
        }
    )


def _grantors_of_database_acl(conn: GreenPlumSession, payload: GrantDatabaseDTO) -> Iterator[str]:
    relation = get_database_acl(conn, payload.name)
    for privilege in parce_acl_rules(relation.acl, final=False):
        if privilege.grantee == payload.role_specification:
            yield privilege.grantor


def grant_on_database(conn: GreenPlumSession, payload: GrantDatabaseDTO) -> None:
    with conn.begin():
        _revoke_database_permissions(conn, payload)

    grantors = []
    if settings.DEEP_REVOKE:
        grantors = list(_grantors_of_database_acl(conn, payload))

    done_with_errors = False
    for grantor in grantors:
        try:
            with conn.begin():
                _revoke_database_permissions(conn, payload, grantor)
        except exc.DatabaseError:
            # У пользователь, который выдал права, может не быть доступа к базе
            done_with_errors = True

    with conn.begin():
        _grant_database_permissions(conn, payload)

    if done_with_errors:
        raise DoneWithErrors(payload.name)

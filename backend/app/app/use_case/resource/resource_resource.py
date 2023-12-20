from typing import List, Optional, Tuple
from sqlalchemy import select, func, join, exc
from sqlalchemy.orm import Session

from app.db.orm_types import GreenPlumConnection, GreenPlumSession
from . import ResourceGroupDTO, ResourceGroupCreateDTO, ResourceGroupUpdateDTO, ResourceGroupAvailableLimitsDTO
from app.use_case.exceptions import DoneWithErrors
from app.read_model import *

_pg_array_agg = func.pg_catalog.array_agg

_gp_resource_group_list_stmt = (
    select([
        gp_resgroup_config.c.groupid.label('oid'),
        gp_resgroup_config.c.groupname.label('name'),
        gp_resgroup_config.c.concurrency,
        gp_resgroup_config.c.cpu_rate_limit,
        gp_resgroup_config.c.memory_limit,
    ])
    .select_from(
        gp_resgroup_config
    )
)

_gp_resource_group_grouped_stmt = (
    select([
        gp_resgroup_config.c.groupid.label('oid'),
        _pg_array_agg(pg_roles.c.rolname).label('group_members'),
    ])
    .select_from(
        gp_resgroup_config
        .outerjoin(pg_roles, gp_resgroup_config.c.groupid == pg_roles.c.rolresgroup)
    )
    .group_by(gp_resgroup_config.c.groupid)
)

_gp_resource_group_stmt = (
    select([
        _gp_resource_group_list_stmt.c.oid,
        _gp_resource_group_list_stmt.c.name,
        _gp_resource_group_list_stmt.c.concurrency,
        _gp_resource_group_list_stmt.c.cpu_rate_limit,
        _gp_resource_group_list_stmt.c.memory_limit,
        _gp_resource_group_grouped_stmt.c.group_members,
    ])
    .select_from(
        join(_gp_resource_group_list_stmt, _gp_resource_group_grouped_stmt,
             _gp_resource_group_list_stmt.c.oid == _gp_resource_group_grouped_stmt.c.oid)
    )
)

_gp_members_of_resource_group_stmt = (
    select([
        gp_resgroup_config.c.groupid.label('oid'),
        gp_resgroup_config.c.groupname.label('name'),
        pg_roles.c.rolname.label('member_rolname'),
    ])
    .select_from(
        gp_resgroup_config
        .join(pg_roles, gp_resgroup_config.c.groupid == pg_roles.c.rolresgroup)
    )
)

_gp_resource_group_available_limits = """
    SELECT
        1 AS cpu_rate_limit_min,
        100 - sum(cpu_rate_limit::integer) AS cpu_rate_limit_max,
        0 AS memory_limit_min,
        100 - sum(memory_limit::integer) AS memory_limit_max,
        0 AS concurrency_min,
        current_setting('max_connections')::integer AS concurrency_max
    FROM gp_toolkit.gp_resgroup_config;
"""


def _calc_create_options(resource_group: ResourceGroupCreateDTO) -> List[str]:
    options = {
        'CPU_RATE_LIMIT': resource_group.cpu_rate_limit,
        'MEMORY_LIMIT': resource_group.memory_limit,
        'CONCURRENCY': resource_group.concurrency,
    }

    options = list(
        map(
            lambda item: f'{item[0]}={item[1]}',
            options.items()
        )
    )

    return options


def _calc_alter_options(resource_group: ResourceGroupUpdateDTO) -> List[str]:
    options = {
        'CPU_RATE_LIMIT': resource_group.cpu_rate_limit,
        'MEMORY_LIMIT': resource_group.memory_limit,
        'CONCURRENCY': resource_group.concurrency,
    }

    options = list(
        map(
            lambda item: f'{item[0]} {item[1]}',
            options.items()
        )
    )

    return options


def _create_resource_group(conn: GreenPlumSession, rsgroup: ResourceGroupCreateDTO) -> None:
    '''
    CREATE RESOURCE GROUP name WITH (group_attribute=value [, ... ])
    where group_attribute is:

    CPU_RATE_LIMIT=integer | CPUSET=tuple
    [ MEMORY_LIMIT=integer ]
    [ CONCURRENCY=integer ]
    [ MEMORY_SHARED_QUOTA=integer ]
    [ MEMORY_SPILL_RATIO=integer ]
    [ MEMORY_AUDITOR= {vmtracker | cgroup} ]
    '''

    options = _calc_create_options(rsgroup)

    sql_command = """
        CREATE RESOURCE GROUP "{name}" WITH ({group_attribute})
    """.format(
        name=rsgroup.name,
        group_attribute=', '.join(options)
    )

    conn.execute(sql_command)


def _alter_resource_group_members(
    conn: GreenPlumSession, rolnames: List[str], rsgname: Optional[str] = None,
) -> None:
    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT('ALTER ROLE "%s" RESOURCE GROUP %s', :rolname, :rsgname);
        END $$
    """

    done_with_errors = False
    for rolname in rolnames:
        try:
            conn.execute(
                sql_command,
                params={
                    "rolname": rolname,
                    "rsgname": f'"{rsgname}"' if rsgname else 'NONE'
                }
            )
        except exc.DatabaseError:
            done_with_errors = True

    if done_with_errors:
        raise DoneWithErrors(rsgname)


def _alter_resource_group(
    conn: GreenPlumSession, rsgname: str, rsgroup: ResourceGroupUpdateDTO,
) -> None:
    '''
    ALTER RESOURCE GROUP name SET group_attribute value
    where group_attribute is one of:

    CONCURRENCY integer
    CPU_RATE_LIMIT integer
    CPUSET tuple
    MEMORY_LIMIT integer
    MEMORY_SHARED_QUOTA integer
    MEMORY_SPILL_RATIO integer
    '''

    options = _calc_alter_options(rsgroup)

    sql_command = """
        ALTER RESOURCE GROUP "{name}" SET {group_attribute}
    """

    # ALTER RESOURCE GROUP cannot be executed from a function or multi-command string
    done_with_errors = False
    for option in options:
        try:
            conn.execute(
                sql_command.format(
                    name=rsgname,
                    group_attribute=option,
                )
            )
        except exc.DatabaseError:
            done_with_errors = True

    if done_with_errors:
        raise DoneWithErrors(rsgname)


def _remove_all_members_from_resource_group(conn: GreenPlumSession, rsgname: str) -> None:
    sql_command = """
        DO $$
        DECLARE
            name_of_role VARCHAR;
            delete_query VARCHAR;
        BEGIN
            FOR name_of_role IN
                SELECT rolname
                FROM pg_roles INNER JOIN pg_resgroup
                    ON pg_roles.rolresgroup = pg_resgroup.oid
                WHERE pg_resgroup.rsgname = :rsgname
            LOOP
                delete_query := FORMAT('ALTER ROLE "%s" RESOURCE GROUP NONE', name_of_role);
                EXECUTE delete_query;
            END LOOP;
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "rsgname": rsgname,
        },
    )


def _terminate_all_queries_with_resource_group(conn: GreenPlumSession, rsgname: str) -> None:
    # For fix RG with name: unknown
    sql_command = """
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE pid <> pg_backend_pid()
            AND rsgid IN (
                SELECT
                    groupid
                FROM
                    gp_toolkit.gp_resgroup_config
                WHERE
                    groupname = :rsgname
            )
    """

    conn.execute(
        sql_command,
        params={
            "rsgname": rsgname,
        },
    )


def _delete_resource_group(conn: GreenPlumSession, rsgname: str) -> None:
    sql_command = f"""
        DROP RESOURCE GROUP "{rsgname}"
    """

    conn.execute(sql_command)


def _get_all_members_of_resource_group(conn: GreenPlumSession, rsname: str) -> List[str]:
    stmt = _gp_members_of_resource_group_stmt.where(
        gp_resgroup_config.c.groupname == rsname
    )
    rows = conn.execute(stmt)

    members = []
    for row in rows:
        members.append(row.member_rolname)

    return members


def _list_of_members_del_and_add(
    conn: GreenPlumSession,
    rsname: str,
    members: List[str],
) -> Tuple[List[str], List[str]]:
    members_in_db = _get_all_members_of_resource_group(conn, rsname)
    to_remove = set(members_in_db) - set(members)
    to_append = set(members) - set(members_in_db)
    return list(to_remove), list(to_append)


def get_all_resource_groups(conn: GreenPlumSession) -> List[ResourceGroupDTO]:
    with conn.begin():
        rows = conn.execute(_gp_resource_group_stmt)
        return [ResourceGroupDTO(**row) for row in rows]


def drop_resource_group(conn: GreenPlumConnection, rsname: str) -> None:
    conn.execution_options(isolation_level="AUTOCOMMIT")
    with Session(conn) as session:
        _remove_all_members_from_resource_group(session, rsname)
        _terminate_all_queries_with_resource_group(session, rsname)
        _delete_resource_group(session, rsname)


def ensure_resource_group(conn: GreenPlumConnection, rsgroup: ResourceGroupCreateDTO) -> None:
    conn.execution_options(isolation_level="AUTOCOMMIT")
    with Session(conn) as session:
        _create_resource_group(session, rsgroup)
        _alter_resource_group_members(session, rsgroup.group_members, rsgroup.name)


def update_resource_group(conn: GreenPlumConnection, rsname: str, rsgroup: ResourceGroupUpdateDTO) -> None:
    conn.execution_options(isolation_level="AUTOCOMMIT")
    with Session(conn) as session:
        removed, appended = _list_of_members_del_and_add(
            session, rsname, rsgroup.group_members
        )

        _alter_resource_group(session, rsname, rsgroup)
        _alter_resource_group_members(session, removed)
        _alter_resource_group_members(session, appended, rsname)


def get_resourse_groups_limits(conn: GreenPlumSession) -> ResourceGroupAvailableLimitsDTO:
    with conn.begin():
        row = conn.execute(_gp_resource_group_available_limits)
        return ResourceGroupAvailableLimitsDTO(**next(row))

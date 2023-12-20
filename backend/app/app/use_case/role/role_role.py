from functools import partial
from typing import List
from sqlalchemy import select

from app.db.orm_types import GreenPlumSession
from . import RoleDTO, RoleCreateDTO, RoleUpdateDTO
from app.use_case.exceptions import NoSuchObject, DoneWithErrors
from app.read_model import *
from app.core.config import settings

_pg_role_stmt = (
    select([
        pg_roles.c.oid,
        pg_roles.c.rolname,
        pg_roles.c.rolsuper,
        pg_roles.c.rolcreaterole,
        pg_roles.c.rolcreatedb,
        pg_roles.c.rolinherit,
        pg_roles.c.rolcanlogin,
    ])
    .select_from(
        pg_roles
    )
)


def _create_role(conn: GreenPlumSession, dbuser: RoleCreateDTO) -> None:
    '''
    CREATE ROLE name [ [ WITH ] option [ ... ] ]

    where option can be:

        SUPERUSER | NOSUPERUSER
        | CREATEDB | NOCREATEDB
        | CREATEROLE | NOCREATEROLE
        | INHERIT | NOINHERIT
        | LOGIN | NOLOGIN
        | REPLICATION | NOREPLICATION
        | BYPASSRLS | NOBYPASSRLS
        | CONNECTION LIMIT connlimit
        | [ ENCRYPTED ] PASSWORD 'password' | PASSWORD NULL
        | VALID UNTIL 'timestamp'
        | IN ROLE role_name [, ...]
        | IN GROUP role_name [, ...]
        | ROLE role_name [, ...]
        | ADMIN role_name [, ...]
        | USER role_name [, ...]
        | SYSID uid
    '''

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'CREATE ROLE "%s" WITH %s %s %s %s %s PASSWORD ''%s''',
                :rolname, :su, :crole, :cdb, :inherit, :login, :passwd
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "rolname": dbuser.rolname,
            "su": 'SUPERUSER' if dbuser.rolsuper else 'NOSUPERUSER',
            "crole": 'CREATEROLE' if dbuser.rolcreaterole else 'NOCREATEROLE',
            "cdb": 'CREATEDB' if dbuser.rolcreatedb else 'NOCREATEDB',
            "inherit": 'INHERIT' if dbuser.rolinherit else 'NOINHERIT',
            "login": 'LOGIN' if dbuser.rolcanlogin else 'NOLOGIN',
            "passwd": dbuser.password,
        },
    )


def _rename_role(conn: GreenPlumSession, rolname: str, dbuser: RoleUpdateDTO) -> None:
    '''
    ALTER ROLE name RENAME TO new_name
    '''

    if rolname == dbuser.rolname:
        return

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'ALTER ROLE "%s" RENAME TO "%s"',
                :oldname, :newname
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "oldname": rolname,
            "newname": dbuser.rolname,
        },
    )


def _alter_role(conn: GreenPlumSession, rolname: str, dbuser: RoleUpdateDTO) -> None:
    '''
    ALTER ROLE role_specification [ WITH ] option [ ... ]

    where option can be:

        SUPERUSER | NOSUPERUSER
        | CREATEDB | NOCREATEDB
        | CREATEROLE | NOCREATEROLE
        | INHERIT | NOINHERIT
        | LOGIN | NOLOGIN
        | REPLICATION | NOREPLICATION
        | BYPASSRLS | NOBYPASSRLS
        | CONNECTION LIMIT connlimit
        | [ ENCRYPTED ] PASSWORD 'password' | PASSWORD NULL
        | VALID UNTIL 'timestamp'
    '''

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'ALTER ROLE "%s" WITH %s %s %s %s %s %s',
                :rolname, :su, :crole, :cdb, :inherit, :login, :passwd
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "rolname": dbuser.rolname,
            "su": 'SUPERUSER' if dbuser.rolsuper else 'NOSUPERUSER',
            "crole": 'CREATEROLE' if dbuser.rolcreaterole else 'NOCREATEROLE',
            "cdb": 'CREATEDB' if dbuser.rolcreatedb else 'NOCREATEDB',
            "inherit": 'INHERIT' if dbuser.rolinherit else 'NOINHERIT',
            "login": 'LOGIN' if dbuser.rolcanlogin else 'NOLOGIN',
            "passwd": f"PASSWORD '{dbuser.password}'" if dbuser.password else "",
        },
    )


def _reassign_all_owned_by_role_v1(conn: GreenPlumSession, dbuser: str) -> None:
    sql_command = """
        DO $$
        DECLARE
            db VARCHAR;
            delete_query VARCHAR;
            connection VARCHAR;
            user_owner VARCHAR;
        BEGIN
            user_owner := (SELECT session_user);
            FOR db IN
                SELECT datname
                FROM pg_database
                WHERE datallowconn = TRUE
            LOOP
                delete_query := FORMAT(
                    'REASSIGN OWNED BY "%s" TO "%s"; DROP OWNED BY "%s"',
                    :dbuser, user_owner, :dbuser
                );
                connection := FORMAT('dbname=''%s''', db);
                PERFORM dblink_exec(connection, delete_query);
            END LOOP;
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "dbuser": dbuser,
        },
    )


def _reassign_all_owned_by_role_v2(conn: GreenPlumSession, dbuser: str) -> None:
    sql_command = """
        DO $$
        DECLARE
            db VARCHAR;
            delete_query VARCHAR;
            connection VARCHAR;
            user_owner VARCHAR;
        BEGIN
            user_owner := (SELECT session_user);
            FOR db IN
                SELECT datname
                FROM pg_database
                WHERE datallowconn = TRUE
            LOOP
                delete_query := FORMAT(
                    'REASSIGN OWNED BY "%s" TO "%s"; DROP OWNED BY "%s"',
                    :dbuser, user_owner, :dbuser
                );
                connection := FORMAT('dbname=''%s'' user=''%s''', db, user_owner);
                PERFORM dblink_exec(connection, delete_query);
            END LOOP;
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "dbuser": dbuser,
        },
    )


def _delete_role(conn: GreenPlumSession, dbuser: str) -> None:
    # Перед удалением, передаем право владения служебной роли
    # без этого будет ошибка: "Role cannot be dropped because some objects depend on it"
    # способ удаления https://dba.stackexchange.com/questions/155332/find-objects-linked-to-a-postgresql-role
    # https://postgrespro.ru/list/thread-id/1442564
    # https://stackoverflow.com/questions/47997897/drop-a-role-with-privileges
    # https://stackoverflow.com/questions/51256454/cannot-drop-postgresql-role-error-cannot-be-dropped-because-some-objects-depe
    # Зависимости хранятся в таблицах: pg_depend, pg_shdepend
    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT('DROP ROLE "%s"', :dbuser);
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "dbuser": dbuser,
        },
    )


def update_role(conn: GreenPlumSession, rolname: str, dbuser: RoleUpdateDTO) -> None:
    with conn.begin():
        _rename_role(conn, rolname, dbuser)
        _alter_role(conn, rolname, dbuser)


def ensure_role(conn: GreenPlumSession, dbuser: RoleCreateDTO) -> None:
    with conn.begin():
        _create_role(conn, dbuser)


def _drop_role_first_var(conn: GreenPlumSession, dbuser: str) -> bool:
    # Первый вариант удаления - просто стараемся удалить
    deleted = False
    try:
        with conn.begin():
            _delete_role(conn, dbuser)
            deleted = True
    finally:
        return deleted


def _drop_role_second_var_v1(conn: GreenPlumSession, dbuser: str) -> bool:
    # Второй вариант - переназначаем права владельца v1
    deleted = False
    try:
        with conn.begin():
            _reassign_all_owned_by_role_v1(conn, dbuser)
            _delete_role(conn, dbuser)
            deleted = True
    finally:
        return deleted


def _drop_role_second_var_v2(conn: GreenPlumSession, dbuser: str) -> bool:
    # Второй вариант - переназначаем права владельца v2
    deleted = False
    try:
        with conn.begin():
            _reassign_all_owned_by_role_v2(conn, dbuser)
            _delete_role(conn, dbuser)
            deleted = True
    finally:
        return deleted


def _install_dblink_if_allow(conn: GreenPlumSession, _dbuser: str) -> bool:
    if not settings.INSTALL_DBLINK:
        return False

    try:
        sql_command = """
            CREATE EXTENSION IF NOT EXISTS dblink
        """

        with conn.begin():
            conn.execute(sql_command)
    finally:
        return False


def drop_role(conn: GreenPlumSession, dbuser: str) -> None:
    drop_vars = (
        partial(x, conn, dbuser)
        for x in (
            _drop_role_first_var,
            _install_dblink_if_allow,
            _drop_role_second_var_v1,
            _drop_role_second_var_v2,
        )
    )

    for drop in drop_vars:
        if drop():
            return

    raise DoneWithErrors(dbuser)


def get_all_roles(conn: GreenPlumSession) -> List[RoleDTO]:
    with conn.begin():
        rows = conn.execute(_pg_role_stmt)
        return [RoleDTO(**row) for row in rows]


def get_role(conn: GreenPlumSession, dbuser: str) -> RoleDTO:
    stmt = _pg_role_stmt.where(pg_roles.c.rolname == dbuser)
    with conn.begin():
        row = conn.execute(stmt).first()
        if row is None:
            raise NoSuchObject(dbuser)
        return RoleDTO(**row)

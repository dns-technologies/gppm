from typing import Iterator, List, Optional
from sqlalchemy import exc

from app.core.config import settings
from app.use_case.exceptions import DoneWithErrors
from app.db.orm_types import GreenPlumSession
from . import GrantTablePrivelegesDTO, GrantTablesInSchemaDTO, GrantTableDTO, GrantTablesInDatabaseDTO
from app.read_model import *
from app.use_case.acl import get_table_acl
from app.use_case.privilege import parce_acl_rules


def _calc_grant_options(privileges: GrantTablePrivelegesDTO) -> List[str]:
    grant_options = {
        'SELECT': privileges.select,
        'INSERT': privileges.insert,
        'UPDATE': privileges.update,
        'DELETE': privileges.delete,
        'TRUNCATE': privileges.truncate,
        'REFERENCES': privileges.references,
        'TRIGGER': privileges.trigger,
    }

    return list(
        map(
            lambda item: item[0],
            filter(lambda item: item[1], grant_options.items())
        )
    )


def _calc_revoke_options(privileges: GrantTablePrivelegesDTO, *, all: bool = False) -> List[str]:
    revoke_options = {
        'SELECT': privileges.select,
        'INSERT': privileges.insert,
        'UPDATE': privileges.update,
        'DELETE': privileges.delete,
        'TRUNCATE': privileges.truncate,
        'REFERENCES': privileges.references,
        'TRIGGER': privileges.trigger,
    }

    if all:
        return revoke_options.keys()

    return list(
        map(
            lambda item: item[0],
            filter(lambda item: not item[1], revoke_options.items())
        )
    )


def _grant_tables_in_database_permissions(conn: GreenPlumSession, payload: GrantTablesInDatabaseDTO) -> None:
    '''
    GRANT { { SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER }
        [, ...] | ALL [ PRIVILEGES ] }
        ON { [ TABLE ] table_name [, ...]
            | ALL TABLES IN SCHEMA schema_name [, ...] }
        TO role_specification [, ...] [ WITH GRANT OPTION ]
    '''

    grant_options = _calc_grant_options(payload.privileges)

    if not grant_options:
        return

    sql_command = """
        DO $$
        DECLARE
            ns VARCHAR;
            query VARCHAR;
        BEGIN
            FOR ns IN 
                SELECT nspname
                FROM pg_namespace
                WHERE nspname <> 'information_schema'
                    AND nspname NOT LIKE 'pg\_%'
                    AND nspname NOT LIKE 'gp\_%'
            LOOP
                query := FORMAT(
                    'GRANT %s ON ALL TABLES IN SCHEMA "%s" TO "%s" %s',
                    :grant_options, ns, :role_specification, :with_grant_option
                );
                EXECUTE query;
            END LOOP;
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grant_options": ', '.join(grant_options),
            "role_specification": payload.role_specification,
            "with_grant_option": 'WITH GRANT OPTION' if payload.with_grant_option else '',
        },
    )


def _grant_tables_in_schema_permissions(conn: GreenPlumSession, payload: GrantTablesInSchemaDTO) -> None:
    '''
    GRANT { { SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER }
        [, ...] | ALL [ PRIVILEGES ] }
        ON { [ TABLE ] table_name [, ...]
            | ALL TABLES IN SCHEMA schema_name [, ...] }
        TO role_specification [, ...] [ WITH GRANT OPTION ]
    '''

    grant_options = _calc_grant_options(payload.privileges)

    if not grant_options:
        return

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'GRANT %s ON ALL TABLES IN SCHEMA "%s" TO "%s" %s',
                :grant_options, :schema_name, :role_specification, :with_grant_option
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grant_options": ', '.join(grant_options),
            "schema_name": payload.db_schema,
            "role_specification": payload.role_specification,
            "with_grant_option": 'WITH GRANT OPTION' if payload.with_grant_option else '',
        },
    )


def _grant_tables_in_schema_permissions_default(conn: GreenPlumSession, payload: GrantTablesInSchemaDTO) -> None:
    '''
    ALTER DEFAULT PRIVILEGES
        [ FOR { ROLE | USER } target_role [, ...] ]
        [ IN SCHEMA schema_name [, ...] ]
        abbreviated_grant_or_revoke

    where abbreviated_grant_or_revoke is one of:

    GRANT { { SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER }
        [, ...] | ALL [ PRIVILEGES ] }
        ON TABLES
        TO { [ GROUP ] role_name | PUBLIC } [, ...] [ WITH GRANT OPTION ]
    '''

    grant_options = _calc_grant_options(payload.privileges)

    if not grant_options:
        return

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'ALTER DEFAULT PRIVILEGES IN SCHEMA "%s" GRANT %s ON TABLES TO "%s" %s',
                :schema_name, :grant_options, :role_specification, :with_grant_option
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grant_options": ', '.join(grant_options),
            "schema_name": payload.db_schema,
            "role_specification": payload.role_specification,
            "with_grant_option": 'WITH GRANT OPTION' if payload.with_grant_option else '',
        },
    )


def _grant_table_permissions(conn: GreenPlumSession, payload: GrantTableDTO) -> None:
    '''
    GRANT { { SELECT | INSERT | UPDATE | REFERENCES } ( column_name [, ...] )
        [, ...] | ALL [ PRIVILEGES ] ( column_name [, ...] ) }
        ON [ TABLE ] table_name [, ...]
        TO role_specification [, ...] [ WITH GRANT OPTION ]
    '''

    grant_options = _calc_grant_options(payload.privileges)

    if not grant_options:
        return

    sql_command = """
        DO $$ BEGIN
            SET ROLE NONE;
            EXECUTE FORMAT(
                'GRANT %s ON TABLE "%s"."%s" TO "%s" %s',
                :grant_options, :schema_name, :table_name, :role_specification, :with_grant_option
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grant_options": ', '.join(grant_options),
            "schema_name": payload.db_schema,
            "table_name": payload.name,
            "role_specification": payload.role_specification,
            "with_grant_option": 'WITH GRANT OPTION' if payload.with_grant_option else '',
        },
    )


def _revoke_tables_in_database_permissions(conn: GreenPlumSession, payload: GrantTablesInDatabaseDTO) -> None:
    '''
    REVOKE [ GRANT OPTION FOR ]
        { { SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER }
        [, ...] | ALL [ PRIVILEGES ] }
        ON { [ TABLE ] table_name [, ...]
            | ALL TABLES IN SCHEMA schema_name [, ...] }
        FROM role_specification [, ...]
        [ CASCADE | RESTRICT ]
    '''

    revoke_options = _calc_revoke_options(payload.privileges)

    if not revoke_options:
        return

    sql_command = """
        DO $$
        DECLARE
            ns VARCHAR;
            query VARCHAR;
        BEGIN
            FOR ns IN 
                SELECT nspname
                FROM pg_namespace
                WHERE nspname <> 'information_schema'
                    AND nspname NOT LIKE 'pg\_%'
                    AND nspname NOT LIKE 'gp\_%'
            LOOP
                query := FORMAT(
                    'REVOKE %s ON ALL TABLES IN SCHEMA "%s" FROM "%s" CASCADE',
                    :revoke_options, ns, :role_specification
                );
                EXECUTE query;
            END LOOP;
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "revoke_options": ', '.join(revoke_options),
            "role_specification": payload.role_specification,
        },
    )


def _revoke_tables_in_schema_permissions(conn: GreenPlumSession, payload: GrantTablesInSchemaDTO) -> None:
    '''
    REVOKE [ GRANT OPTION FOR ]
        { { SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER }
        [, ...] | ALL [ PRIVILEGES ] }
        ON { [ TABLE ] table_name [, ...]
            | ALL TABLES IN SCHEMA schema_name [, ...] }
        FROM role_specification [, ...]
        [ CASCADE | RESTRICT ]
    '''

    revoke_options = _calc_revoke_options(payload.privileges)

    if not revoke_options:
        return

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'REVOKE %s ON ALL TABLES IN SCHEMA "%s" FROM "%s" CASCADE',
                :revoke_options, :schema_name, :role_specification
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "revoke_options": ', '.join(revoke_options),
            "schema_name": payload.db_schema,
            "role_specification": payload.role_specification,
        }
    )


def _revoke_tables_in_schema_permissions_default(conn: GreenPlumSession, payload: GrantTablesInSchemaDTO) -> None:
    '''
    ALTER DEFAULT PRIVILEGES
        [ FOR { ROLE | USER } target_role [, ...] ]
        [ IN SCHEMA schema_name [, ...] ]
        abbreviated_grant_or_revoke

    where abbreviated_grant_or_revoke is one of:

    REVOKE [ GRANT OPTION FOR ]
        { { SELECT | INSERT | UPDATE | DELETE | TRUNCATE | REFERENCES | TRIGGER }
        [, ...] | ALL [ PRIVILEGES ] }
        ON TABLES
        FROM { [ GROUP ] role_name | PUBLIC } [, ...]
        [ CASCADE | RESTRICT ]
    '''

    revoke_options = _calc_revoke_options(payload.privileges)

    if not revoke_options:
        return

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'ALTER DEFAULT PRIVILEGES IN SCHEMA "%s" REVOKE %s ON TABLES FROM "%s" CASCADE',
                :schema_name, :revoke_options, :role_specification
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "revoke_options": ', '.join(revoke_options),
            "schema_name": payload.db_schema,
            "role_specification": payload.role_specification,
        }
    )


def _revoke_table_permissions(conn: GreenPlumSession, payload: GrantTableDTO, grantor: Optional[str] = None) -> None:
    '''
    REVOKE [ GRANT OPTION FOR ]
        { { SELECT | INSERT | UPDATE | REFERENCES } ( column_name [, ...] )
        [, ...] | ALL [ PRIVILEGES ] ( column_name [, ...] ) }
        ON [ TABLE ] table_name [, ...]
        FROM role_specification [, ...]
        [ CASCADE | RESTRICT ]
    '''

    revoke_options = _calc_revoke_options(payload.privileges, all=True)

    if not revoke_options:
        return

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT('SET ROLE %s', :grantor);
            EXECUTE FORMAT(
                'REVOKE %s ON TABLE "%s"."%s" FROM "%s" CASCADE',
                :revoke_options, :schema_name, :table_name, :role_specification
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grantor": f'"{grantor}"' if grantor else 'NONE',
            "revoke_options": ', '.join(revoke_options),
            "schema_name": payload.db_schema,
            "table_name": payload.name,
            "role_specification": payload.role_specification,
        }
    )


def _grantors_of_table_acl(conn: GreenPlumSession, payload: GrantTableDTO) -> Iterator[str]:
    relation = get_table_acl(conn, payload.db_schema, payload.name)
    for privilege in parce_acl_rules(relation.acl, final=False):
        if privilege.grantee == payload.role_specification:
            yield privilege.grantor


def grant_all_tables_in_database(conn: GreenPlumSession, payload: GrantTablesInDatabaseDTO) -> None:
    with conn.begin():
        _revoke_tables_in_database_permissions(conn, payload)
        _grant_tables_in_database_permissions(conn, payload)


def grant_all_tables_in_schema(conn: GreenPlumSession, payload: GrantTablesInSchemaDTO) -> None:
    with conn.begin():
        _revoke_tables_in_schema_permissions(conn, payload)
        _grant_tables_in_schema_permissions(conn, payload)

    with conn.begin():
        _revoke_tables_in_schema_permissions_default(conn, payload)
        _grant_tables_in_schema_permissions_default(conn, payload)


def grant_on_table(conn: GreenPlumSession, payload: GrantTableDTO) -> None:
    with conn.begin():
        _revoke_table_permissions(conn, payload)

    grantors = []
    if settings.DEEP_REVOKE:
        grantors = list(_grantors_of_table_acl(conn, payload))

    done_with_errors = False
    for grantor in grantors:
        try:
            with conn.begin():
                _revoke_table_permissions(conn, payload, grantor)
        except exc.DatabaseError:
            # У пользователь, который выдал права, может не быть доступа к таблице
            done_with_errors = True

    with conn.begin():
        _grant_table_permissions(conn, payload)

    if done_with_errors:
        raise DoneWithErrors(payload.name)

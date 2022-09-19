from typing import Iterator, List, Optional
from sqlalchemy import exc
from app.core.config import settings
from app.use_case.exceptions import DoneWithErrors

from app.db.orm_types import GreenPlumSession

from . import GrantSchemaDTO, GrantSchemaPrivelegesDTO, GrantSchemasInDatabaseDTO
from app.read_model import *
from app.use_case.acl import get_schema_acl
from app.use_case.privilege import parce_acl_rules


def _calc_grant_options(privileges: GrantSchemaPrivelegesDTO) -> List[str]:
    grant_options = {
        'CREATE': privileges.create,
        'USAGE': privileges.usage,
    }

    return list(
        map(
            lambda item: item[0],
            filter(lambda item: item[1], grant_options.items())
        )
    )


def _calc_revoke_options(privileges: GrantSchemaPrivelegesDTO, *, all: bool = False) -> List[str]:
    revoke_options = {
        'CREATE': privileges.create,
        'USAGE': privileges.usage,
    }

    if all:
        return revoke_options.keys()

    return list(
        map(
            lambda item: item[0],
            filter(lambda item: not item[1], revoke_options.items())
        )
    )


def _grant_schemas_in_database_permissions(conn: GreenPlumSession, payload: GrantSchemasInDatabaseDTO):
    '''
    GRANT { { CREATE | USAGE } [, ...] | ALL [ PRIVILEGES ] }
        ON SCHEMA schema_name [, ...]
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
                    'GRANT %s ON SCHEMA "%s" TO "%s" %s',
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


def _grant_schema_permissions(conn: GreenPlumSession, payload: GrantSchemaDTO):
    '''
    GRANT { { CREATE | USAGE } [, ...] | ALL [ PRIVILEGES ] }
        ON SCHEMA schema_name [, ...]
        TO role_specification [, ...] [ WITH GRANT OPTION ]
    '''

    grant_options = _calc_grant_options(payload.privileges)

    if not grant_options:
        return

    sql_command = """
        DO $$ BEGIN
            SET ROLE NONE;
            EXECUTE FORMAT(
                'GRANT %s ON SCHEMA "%s" TO "%s" %s',
                :grant_options, :schema_name, :role_specification, :with_grant_option
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grant_options": ', '.join(grant_options),
            "schema_name": payload.name,
            "role_specification": payload.role_specification,
            "with_grant_option": 'WITH GRANT OPTION' if payload.with_grant_option else '',
        }
    )


def _revoke_schemas_in_database_permissions(conn: GreenPlumSession, payload: GrantSchemasInDatabaseDTO):
    '''
    REVOKE [ GRANT OPTION FOR ]
        { { CREATE | USAGE } [, ...] | ALL [ PRIVILEGES ] }
        ON SCHEMA schema_name [, ...]
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
                    'REVOKE %s ON SCHEMA "%s" FROM "%s" CASCADE',
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


def _revoke_schema_permissions(conn: GreenPlumSession, payload: GrantSchemaDTO, grantor: Optional[str] = None):
    '''
    REVOKE [ GRANT OPTION FOR ]
        { { CREATE | USAGE } [, ...] | ALL [ PRIVILEGES ] }
        ON SCHEMA schema_name [, ...]
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
                'REVOKE %s ON SCHEMA "%s" FROM "%s" CASCADE',
                :revoke_options, :schema_name, :role_specification
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "grantor": f'"{grantor}"' if grantor else 'NONE',
            "revoke_options": ', '.join(revoke_options),
            "schema_name": payload.name,
            "role_specification": payload.role_specification,
        },
    )


def _grantors_of_schema_acl(conn: GreenPlumSession, payload: GrantSchemaDTO) -> Iterator[str]:
    relation = get_schema_acl(conn, payload.name)
    for privilege in parce_acl_rules(relation.acl, final=False):
        if privilege.grantee == payload.role_specification:
            yield privilege.grantor


def grant_all_schemas_in_database(conn: GreenPlumSession, payload: GrantSchemasInDatabaseDTO):
    with conn.begin():
        _revoke_schemas_in_database_permissions(conn, payload)
        _grant_schemas_in_database_permissions(conn, payload)


def grant_on_schema(conn: GreenPlumSession, payload: GrantSchemaDTO):
    with conn.begin():
        _revoke_schema_permissions(conn, payload)

    grantors = []
    if settings.DEEP_REVOKE:
        grantors = list(_grantors_of_schema_acl(conn, payload))

    done_with_errors = False
    for grantor in grantors:
        try:
            with conn.begin():
                _revoke_schema_permissions(conn, payload, grantor)
        except exc.DatabaseError:
            # У пользователь, который выдал права, может не быть доступа к схеме
            done_with_errors = True

    with conn.begin():
        _grant_schema_permissions(conn, payload)

    if done_with_errors:
        raise DoneWithErrors(payload.name)

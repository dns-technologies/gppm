from typing import List
from sqlalchemy import cast, select, ARRAY, Text

from app.db.orm_types import GreenPlumSession

from app.read_model import *
from .import DefaultPermissonsDTO, RevokeAllDefaultsDTO
from app.use_case.privilege import parce_acl_rules
from app.use_case.exceptions import TypeNotImplemented

_type_of_def_entries = {
    'Relation': 'r',
    'Sequence': 'S',
    'Function': 'f',
    'Type': 'T',
    'Schema': 'n',
}

_type_of_def_entries_inv = {
    v: k for k, v in _type_of_def_entries.items()
}

_entrie_to_object = {
    'Relation': 'TABLES',
    'Sequence': 'SEQUENCES',
    'Function': 'FUNCTIONS',
    'Type': 'TYPES',
    'Schema': 'SCHEMAS',
}

_pg_default_permission = (
    select([
        pg_namespace.c.nspname.label('schema'),
        pg_default_acl.c.defaclobjtype.label('objtype'),
        cast(pg_default_acl.c.defaclacl, ARRAY(Text)).label('defaclacl'),
    ])
    .select_from(
        pg_default_acl
        .outerjoin(pg_namespace, pg_default_acl.c.defaclnamespace == pg_namespace.c.oid)
    )
)


def _entrie2object(entrie: str) -> str:
    try:
        return _entrie_to_object[entrie]
    except KeyError:
        raise TypeNotImplemented(entrie)


def _revoke_default_permissions(conn: GreenPlumSession, payload: RevokeAllDefaultsDTO):
    '''
    ALTER DEFAULT PRIVILEGES
        [ FOR { ROLE | USER } target_role [, ...] ]
        [ IN SCHEMA schema_name [, ...] ]
    REVOKE [ GRANT OPTION FOR ]
        { ALL [ PRIVILEGES ] }
        ON { TABLES | SEQUENCES | FUNCTIONS | TYPES | SCHEMAS }
        FROM { [ GROUP ] role_name | PUBLIC } [, ...]
        [ CASCADE | RESTRICT ]
    '''

    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT(
                'ALTER DEFAULT PRIVILEGES FOR ROLE "%s" %s REVOKE ALL ON %s FROM "%s" CASCADE',
                :target_role, :schema_path, :entrie_type, :role_specification
            );
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "target_role": payload.target_role,
            "schema_path": f'IN SCHEMA "{payload.db_schema}"' if payload.db_schema else '',
            "entrie_type": _entrie2object(payload.entrie_type),
            "role_specification": payload.role_specification
        }
    )


def revoke_all_default_permissions(conn: GreenPlumSession, payload: RevokeAllDefaultsDTO):
    with conn.begin():
        _revoke_default_permissions(conn, payload)


def get_all_default_permissions(conn: GreenPlumSession) -> List[DefaultPermissonsDTO]:
    with conn.begin():
        rows = conn.execute(_pg_default_permission)
        return [
            DefaultPermissonsDTO(
                schema=row.schema,
                objtype=_type_of_def_entries_inv.get(row.objtype),
                defaclacl=list(parce_acl_rules(row.defaclacl, final=False)),
            ) for row in rows
        ]

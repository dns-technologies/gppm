from typing import List, Optional
from sqlalchemy import cast, select, ARRAY, Text, func
from sqlalchemy.sql import Select

from app.db.orm_types import GreenPlumSession
from . import TableAclDTO
from app.use_case.exceptions import NoSuchObject
from app.read_model import *


_pg_table_is_visible = func.pg_catalog.pg_table_is_visible


_pg_class_stmt = (
    select([
        pg_class.c.oid,
        pg_namespace.c.nspname.label('schema'),
        pg_class.c.relname.label('name'),
        pg_roles.c.rolname.label('owner'),
        cast(pg_class.c.relacl, ARRAY(Text)).label('acl'),
    ])
    .select_from(
        pg_class
        .outerjoin(pg_namespace, pg_class.c.relnamespace == pg_namespace.c.oid)
        .outerjoin(pg_roles, pg_class.c.relowner == pg_roles.c.oid)
    )
)


def _table_stmt(schema: Optional[str] = None, table_name: Optional[str] = None) -> Select:
    stmt = _filter_pg_class_stmt(
        _pg_class_stmt, schema=schema, rel_name=table_name)
    return stmt.where(pg_class.c.relkind.in_([
        PgRelKind.TABLE.value,
        PgRelKind.VIEW.value,
        PgRelKind.MATERIALIZED_VIEW.value,
        PgRelKind.PARTITIONED_TABLE.value,
        PgRelKind.FOREIGN_TABLE.value,
    ]))


def _filter_pg_class_stmt(stmt, schema: Optional[str] = None, rel_name: Optional[str] = None) -> Select:
    if schema is not None:
        stmt = stmt.where(pg_namespace.c.nspname == schema)

    if rel_name is not None:
        if schema is None:
            stmt = stmt.where(_pg_table_is_visible(pg_class.c.oid))

        stmt = stmt.where(pg_class.c.relname == rel_name)

    return stmt


def get_all_table_acls(conn: GreenPlumSession, schema: str) -> List[TableAclDTO]:
    stmt = _table_stmt(schema=schema)
    with conn.begin():
        rows = conn.execute(stmt)
        return [TableAclDTO(**row) for row in rows]


def get_table_acl(conn: GreenPlumSession, schema: str, table: str) -> TableAclDTO:
    stmt = _table_stmt(schema=schema, table_name=table)
    with conn.begin():
        row = conn.execute(stmt).first()
        if row is None:
            raise NoSuchObject(table)
        return TableAclDTO(**row)

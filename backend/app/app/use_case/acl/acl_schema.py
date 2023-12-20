from typing import List
from sqlalchemy import cast, select, ARRAY, Text, and_, not_

from app.db.orm_types import GreenPlumSession
from . import SchemaAclDTO
from app.use_case.exceptions import NoSuchObject
from app.read_model import *

# Системные таблицы фильтруются по префиксу
# это надежно, т.к. пользователь не может создать схемы с префиксами pg_ и gp_
# Получит ошибку: The prefix "gp_" is reserved for system schemas.
_pg_schema_stmt = (
    select([
        pg_namespace.c.oid,
        pg_namespace.c.nspname.label('name'),
        pg_roles.c.rolname.label('owner'),
        cast(pg_namespace.c.nspacl, ARRAY(Text)).label('acl'),
    ])
    .select_from(
        pg_namespace
        .outerjoin(pg_roles, pg_namespace.c.nspowner == pg_roles.c.oid)
    )
    .where(
        and_(
            pg_namespace.c.nspname != 'information_schema',
            not_(pg_namespace.c.nspname.startswith('pg\_')),
            not_(pg_namespace.c.nspname.startswith('gp\_'))
        )
    )
)


def get_all_schema_acls(conn: GreenPlumSession) -> List[SchemaAclDTO]:
    with conn.begin():
        rows = conn.execute(_pg_schema_stmt)
        return [SchemaAclDTO(**row) for row in rows]


def get_schema_acl(conn: GreenPlumSession, schema: str) -> SchemaAclDTO:
    stmt = _pg_schema_stmt.where(pg_namespace.c.nspname == schema)
    with conn.begin():
        row = conn.execute(stmt).first()
        if row is None:
            raise NoSuchObject(schema)
        return SchemaAclDTO(**row)

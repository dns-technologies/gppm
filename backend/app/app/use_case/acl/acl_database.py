from typing import List
from sqlalchemy import cast, select, ARRAY, Text

from app.db.orm_types import GreenPlumSession
from . import DatabaseAclDTO
from app.use_case.exceptions import NoSuchObject
from app.read_model import *


_pg_db_stmt = (
    select([
        pg_database.c.oid,
        pg_database.c.datname.label('name'),
        pg_roles.c.rolname.label('owner'),
        cast(pg_database.c.datacl, ARRAY(Text)).label('acl'),
    ])
    .select_from(
        pg_database
        .outerjoin(pg_roles, pg_database.c.datdba == pg_roles.c.oid)
    )
    .where(pg_database.c.datistemplate == False)
)


def get_all_database_acls(conn: GreenPlumSession) -> List[DatabaseAclDTO]:
    with conn.begin():
        rows = conn.execute(_pg_db_stmt)
        return [DatabaseAclDTO(**row) for row in rows]


def get_database_acl(conn: GreenPlumSession, database: str) -> DatabaseAclDTO:
    stmt = _pg_db_stmt.where(pg_database.c.datname == database)
    with conn.begin():
        row = conn.execute(stmt).first()
        if row is None:
            raise NoSuchObject(database)
        return DatabaseAclDTO(**row)

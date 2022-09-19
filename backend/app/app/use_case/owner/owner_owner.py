from app.db.orm_types import GreenPlumSession

from . import UpdateOwnerDTO
from app.use_case.exceptions import TypeNotImplemented
from app.read_model import *


def _change_database_owner(conn: GreenPlumSession, payload: UpdateOwnerDTO):
    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT('ALTER DATABASE "%s" OWNER TO "%s"', :database_name, :new_owner);
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "database_name": payload.database,
            "new_owner": payload.owner,
        },
    )


def _change_schema_owner(conn: GreenPlumSession, payload: UpdateOwnerDTO):
    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT('ALTER SCHEMA "%s" OWNER TO "%s"', :schema_name, :new_owner);
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "schema_name": payload.db_schema,
            "new_owner": payload.owner,
        },
    )


def _change_table_owner(conn: GreenPlumSession, payload: UpdateOwnerDTO):
    sql_command = """
        DO $$ BEGIN
            EXECUTE FORMAT('ALTER TABLE "%s"."%s" OWNER TO "%s"', :schema_name, :table_name, :new_owner);
        END $$
    """

    conn.execute(
        sql_command,
        params={
            "schema_name": payload.db_schema,
            "table_name": payload.table,
            "new_owner": payload.owner,
        },
    )


def update_owner(conn: GreenPlumSession, payload: UpdateOwnerDTO):
    like_switch = {
        "database": _change_database_owner,
        "schema": _change_schema_owner,
        "table": _change_table_owner
    }

    callback_update_owner = like_switch.get(payload.type_of_entity)
    if callback_update_owner is None:
        raise TypeNotImplemented("It is not possible to change the owner of this entity type")

    with conn.begin():
        callback_update_owner(conn, payload)

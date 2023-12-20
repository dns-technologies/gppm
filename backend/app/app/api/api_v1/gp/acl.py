from typing import Any, List
from fastapi import APIRouter, Depends

from app.db.orm_types import GreenPlumSession
import app.use_case.acl as acl
from app.api.deps import get_current_active_user, get_greenplum_session
import app.schemas as schemas
import app.models as models

router = APIRouter()


@router.get("/databases", response_model=List[schemas.Database])
def read_acl_databases(
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Return all ACL permissions about all databases.
    """

    return acl.get_all_database_acls(db)


@router.get("/schemas", response_model=List[schemas.Schema])
def read_acl_schemas(
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Return all ACL permissions about all schemas in a specific database.
    """

    return acl.get_all_schema_acls(db)


@router.get("/schemas/{schema}/tables", response_model=List[schemas.Table])
def read_acl_tables(
    schema: str,
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Return all ACL permissions about all tables in a specific database and shema.
    """

    return acl.get_all_table_acls(db, schema)

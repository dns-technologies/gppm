from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException

from app.db.orm_types import GreenPlumSession
import app.use_case.privilege as privilege
import app.use_case.privilege_graph as privilege_graph
from app.api.deps import (
    get_current_active_access,
    get_current_active_user,
    get_greenplum_session,
)
import app.schemas as schemas
import app.models as models

router = APIRouter()


@router.get("/decode/rule", response_model=schemas.Privilege)
def decode_one_acl_rule(
    acl_rule: str,
) -> Any:
    """
    Decode one ACL rule into array of permissions.
    """

    return privilege.parce_one_acl_rule(acl_rule)


@router.post("/decode/rules", response_model=List[schemas.Privilege])
def decode_acl_rules(
    *,
    acl_rules: schemas.ACLRule,
) -> Any:
    """
    Decode several ACL rules into two dimensional array of permissions.
    """

    return privilege.parce_acl_rules(acl_rules.acls)


@router.put("/grant-on/database", response_model=schemas.Msg)
def grant_on_database(
    *,
    grant_options: schemas.GrantDatabase,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Grant and revoke permissions of a database.
    """

    accessed = bool(list(filter(
        lambda x: x.database == grant_options.name and x.db_schema is None,
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    privilege.grant_on_database(db, grant_options)
    return {"msg": "Permissions have been granted successfully."}


@router.put("/grant-on/schema", response_model=schemas.Msg)
def grant_on_schema(
    *,
    grant_options: schemas.GrantSchema,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Grant and revoke permissions of a schema.
    """

    accessed = bool(list(filter(
        lambda x: x.database == grant_options.database and (
            x.db_schema is None or x.db_schema == grant_options.name
        ),
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    privilege.grant_on_schema(db, grant_options)
    return {"msg": "Permissions have been granted successfully."}


@router.put("/grant-on/schema/in-database", response_model=schemas.Msg)
def grant_on_schemas_in_database(
    *,
    grant_options: schemas.GrantSchemasInDatabase,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Grant and revoke permissions of all schemas in database.
    """

    accessed = bool(list(filter(
        lambda x: x.database == grant_options.database and x.db_schema is None,
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    privilege.grant_all_schemas_in_database(db, grant_options)
    return {"msg": "Permissions have been granted successfully."}


@router.put("/grant-on/table", response_model=schemas.Msg)
def grant_on_table(
    *,
    grant_options: schemas.GrantTable,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Grant and revoke permissions of a table.
    """

    accessed = bool(list(filter(
        lambda x: x.database == grant_options.database and (
            x.db_schema is None or x.db_schema == grant_options.db_schema
        ),
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    privilege.grant_on_table(db, grant_options)
    return {"msg": "Permissions have been granted successfully."}


@router.put("/grant-on/table/in-schema", response_model=schemas.Msg)
def grant_on_tables_in_schema(
    *,
    grant_options: schemas.GrantTablesInSchema,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Grant and revoke permissions of all tables in schema.
    """

    accessed = bool(list(filter(
        lambda x: x.database == grant_options.database and (
            x.db_schema is None or x.db_schema == grant_options.db_schema
        ),
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    privilege.grant_all_tables_in_schema(db, grant_options)
    return {"msg": "Permissions have been granted successfully."}


@router.put("/grant-on/table/in-database", response_model=schemas.Msg)
def grant_on_tables_in_database(
    *,
    grant_options: schemas.GrantTablesInDatabase,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Grant and revoke permissions of all tables in all schemas in database.
    """

    accessed = bool(list(filter(
        lambda x: x.database == grant_options.database and x.db_schema is None,
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    privilege.grant_all_tables_in_database(db, grant_options)
    return {"msg": "Permissions have been granted successfully."}


@router.post("/graph-permissions", response_model=List[schemas.Privilege])
def read_graph_acl_permissions(
    *,
    graph_info: schemas.GraphPermissions,
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Return all graph ACL permissions for each object on a server.
    """

    return privilege_graph.get_all_graph_permissions(db, graph_info)


@router.get("/default-permissions", response_model=List[schemas.DefaultPermissions])
def read_default_acl_permissions(
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Return all default ACL permissions for each object on a server.
    """

    return privilege_graph.get_all_default_permissions(db)


@router.put("/default-revoke-on/all", response_model=schemas.Msg)
def revoke_defaults_on_all(
    *,
    revoke_options: schemas.RevokeAllDefaults,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Revoke default permissions of all type of objects on a server.
    """

    accessed = bool(list(filter(
        lambda x: x.database == revoke_options.database and (
            x.db_schema is None or x.db_schema == revoke_options.db_schema
        ),
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    privilege_graph.revoke_all_default_permissions(db, revoke_options)
    return {"msg": "Permissions have been revoke successfully."}

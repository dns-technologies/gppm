from typing import Any, List
from fastapi import APIRouter, Depends
from app.db.orm_types import GreenPlumConnection, GreenPlumSession
import app.use_case.resource as resource
from app.api.deps import (
    get_current_active_user,
    get_current_active_superuser,
    get_greenplum_connection,
    get_greenplum_session,
)
import app.schemas as schemas
import app.models as models

router = APIRouter()


@router.get("", response_model=List[schemas.ResourceGroup])
def read_resource_groups(
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Get all resource groups in a server.
    """

    return resource.get_all_resource_groups(db)


@router.get("/available-limits", response_model=schemas.ResourceGroupAvailableLimits)
def read_available_limits_for_resource_groups(
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Get available limits for resource group create or modify.
    """

    return resource.get_resourse_groups_limits(db)


@router.post("", response_model=schemas.Msg)
def create_resource_group(
    *,
    resource_group_in: schemas.ResourceGroupCreate,
    current_user: models.User = Depends(get_current_active_superuser),
    db: GreenPlumConnection = Depends(get_greenplum_connection),
) -> Any:
    """
    Create resource group with params and members.
    """

    resource.ensure_resource_group(db, resource_group_in)
    return {"msg": "The resource group with this name was successfully created."}


@router.put("/{resource_group}/one", response_model=schemas.Msg)
def update_resource_group(
    *,
    resource_group: str,
    resource_group_in: schemas.ResourceGroupUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
    db: GreenPlumConnection = Depends(get_greenplum_connection),
) -> Any:
    """
    Update a specific resource group.
    """

    resource.update_resource_group(db, resource_group, resource_group_in)
    return {"msg": "The resource group with this name was successfully updated."}


@router.delete("/{resource_group}/one", response_model=schemas.Msg)
def delete_resource_group(
    *,
    resource_group: str,
    current_user: models.User = Depends(get_current_active_superuser),
    db: GreenPlumConnection = Depends(get_greenplum_connection),
) -> Any:
    """
    Delete a specific resource group by it name.
    """

    resource.drop_resource_group(db, resource_group)
    return {"msg": "The resource group with this name was successfully deleted."}

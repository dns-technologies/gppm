from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException

from app.db.orm_types import GreenPlumSession
import app.use_case.role as role
from app.api.deps import (
    get_current_active_access,
    get_current_active_user,
    get_current_active_superuser,
    get_greenplum_session,
)
import app.schemas as schemas
import app.models as models

router = APIRouter()


@router.get("", response_model=List[schemas.Role])
def read_roles(
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Get all roles in a server.
    """

    return role.get_all_roles(db)


@router.get("/graph", response_model=schemas.RoleGraph)
def read_roles_as_graph(
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Return all roles presents as a graph.
    """

    return role.get_graph_of_members(db)


@router.get("/{rolname}/members", response_model=List[schemas.RoleMember])
def read_members_by_role(
    rolname: str,
    current_user: models.User = Depends(get_current_active_user),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Return array of members included in a specific role.
    """

    return role.get_role_members(db, rolname)


@router.delete("/{rolname}/members/{member}/one", response_model=schemas.Msg)
def remove_member_from_role(
    *,
    rolname: str,
    member: str,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Remove one member from a specific role.
    """

    accessed = bool(list(filter(
        lambda x: x.role == rolname,
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    role.remove_member_from_role(db, rolname, member)
    return {"msg": "The member was successfully deleted from this rolname."}


@router.put("/{rolname}/members/{member}/one", response_model=schemas.Msg)
def append_member_to_role(
    *,
    rolname: str,
    member: str,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Append one member into a specific role.
    """

    accessed = bool(list(filter(
        lambda x: x.role == rolname,
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    role.append_member_to_role(db, rolname, member)
    return {"msg": "The member was successfully appended to this rolname."}


@router.post("", response_model=schemas.Msg)
def create_role(
    *,
    role_in: schemas.RoleCreate,
    current_user: models.User = Depends(get_current_active_superuser),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Create role with params.
    """

    role.ensure_role(db, role_in)
    return {"msg": "The role with this rolname was successfully created."}


@router.put("/{rolname}/one", response_model=schemas.Msg)
def update_role(
    *,
    rolname: str,
    role_in: schemas.RoleUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Update a specific role.
    """

    role.update_role(db, rolname, role_in)
    return {"msg": "The role with this rolname was successfully updated."}


@router.delete("/{rolname}/one", response_model=schemas.Msg)
def delete_role(
    *,
    rolname: str,
    current_user: models.User = Depends(get_current_active_superuser),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Delete a specific role by name.
    """

    role.drop_role(db, rolname)
    return {"msg": "The role with this rolname was successfully deleted."}

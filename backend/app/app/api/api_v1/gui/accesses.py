from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
import app.models as models
from app.api import deps

router = APIRouter()


@router.get("", response_model=List[schemas.Access])
def read_access(
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve access rule.
    """

    return crud.access.get_all(db)


@router.post("", response_model=schemas.Access)
def create_access(
    *,
    access_in: schemas.AccessCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Create new access rule.
    """

    return crud.access.create(db, obj_in=access_in)


@router.get("/{access_id}/one", response_model=schemas.Access)
def read_access_by_id(
    access_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific access rule by id.
    """

    access = crud.access.get(db, id=access_id)
    if not access:
        raise HTTPException(
            status_code=404,
            detail="The access rule with this id does not exist in the system",
        )
    return access


@router.put("/{access_id}/one", response_model=schemas.Access)
def update_access(
    *,
    access_id: int,
    access_in: schemas.AccessUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Update a access rule.
    """

    access = crud.access.get(db, id=access_id)
    if not access:
        raise HTTPException(
            status_code=404,
            detail="The access rule with this id does not exist in the system",
        )
    access = crud.access.update(db, db_obj=access, obj_in=access_in)
    return access


@router.delete("/{access_id}/one", response_model=schemas.Access)
def delete_access(
    *,
    access_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete a access rule.
    """

    access = crud.access.get(db, id=access_id)
    if not access:
        raise HTTPException(
            status_code=404,
            detail="The access rule with this id does not exist in the system",
        )
    access = crud.access.remove(db, db_obj=access)
    return access

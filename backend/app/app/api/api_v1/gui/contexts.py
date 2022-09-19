from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
import app.crud as crud
import app.schemas as schemas
import app.models as models
from app.api import deps
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=List[schemas.Context])
def read_contexts(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve contexts.
    """

    return crud.context.get_all(db)


@router.post("/validate", response_model=bool)
def validate_context(
    *,
    context_in: schemas.ContextMini,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Checking the context for validity.
    """

    return crud.context.validate(db, obj_in=context_in)


@router.post("", response_model=schemas.Context)
def create_context(
    *,
    context_in: schemas.ContextCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Create new context.
    """

    return crud.context.create(db, obj_in=context_in)


@router.put("/{context_id}/one", response_model=schemas.Context)
def update_context(
    *,
    context_id: int,
    context_in: schemas.ContextUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Update a context.
    """

    context = crud.context.get(db, id=context_id)
    if not context:
        raise HTTPException(
            status_code=404,
            detail="The context with this id does not exist in the system",
        )
    context = crud.context.update(db, db_obj=context, obj_in=context_in)
    return context


@router.delete("/{context_id}/one", response_model=schemas.Context)
def delete_context(
    *,
    context_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete a context.
    """

    context = crud.context.get(db, id=context_id)
    if not context:
        raise HTTPException(
            status_code=404,
            detail="The context with this id does not exist in the system",
        )
    context = crud.context.remove(db, db_obj=context)
    return context

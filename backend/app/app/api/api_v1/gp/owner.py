from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from app.db.orm_types import GreenPlumSession
import app.use_case.owner as owner
from app.api.deps import (
    get_current_active_access,
    get_current_active_user,
    get_greenplum_session,
)
import app.schemas as schemas
import app.models as models

router = APIRouter()


@router.put("", response_model=schemas.Msg)
def change_entity_owner(
    *,
    owner_options: schemas.OwnerEntityUpdate,
    current_user: models.User = Depends(get_current_active_user),
    current_access: List[models.Access] = Depends(get_current_active_access),
    db: GreenPlumSession = Depends(get_greenplum_session),
) -> Any:
    """
    Change the owner of the selected entity.
    """

    accessed = bool(list(filter(
        lambda x: x.database == owner_options.database and (
            x.db_schema is None or x.db_schema == owner_options.db_schema
        ),
        current_access
    ))) if not current_user.is_superuser else True

    if not accessed:
        raise HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges"
        )

    owner.update_owner(db, owner_options)
    return {"msg": "The owner of the entity has been successfully changed."}

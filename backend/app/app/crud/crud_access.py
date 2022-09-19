from typing import Any, Dict, Union

from sqlalchemy.orm import Session

from app.crud.crud_base import CRUDBase
from app.models.access import Access
from app.schemas.access import AccessCreate, AccessUpdate


class CRUDAccess(CRUDBase[Access, AccessCreate, AccessUpdate]):
    def create(self, db: Session, *, obj_in: AccessCreate) -> Access:
        db_obj = Access(
            context_id=obj_in.context_id,
            user_id=obj_in.user_id,
            role=obj_in.role,
            database=obj_in.database,
            db_schema=obj_in.db_schema,
            is_active=obj_in.is_active,
        )
        return super().create(db, obj_in=db_obj)

    def update(
        self, db: Session, *, db_obj: Access, obj_in: Union[AccessUpdate, Dict[str, Any]]
    ) -> Access:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove(
        self, db: Session, *, db_obj: Access
    ) -> Access:
        return super().remove(db, id=db_obj.id)

    def is_active(self, access: Access) -> bool:
        return access.is_active


access = CRUDAccess(Access)

from typing import Dict, Optional
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings
import app.crud as crud


class BaseAuth:
    def auth(self, email: str, password: str, *, db: Session) -> Optional[User]:
        return None

    def update_db(self, payload: Dict, *, db: Session) -> Optional[User]:
        email = payload.get("email")
        user = crud.user.get_by_email(db, email=email)

        try:
            if not user and settings.AUTH_OPEN_REGISTRATION:
                newUser = UserCreate(**payload)
                user = crud.user.create(db, obj_in=newUser)
            if user and settings.AUTH_REFRESH_PASSWORD:
                updatedUser = UserUpdate(**payload)
                user = crud.user.update(db, db_obj=user, obj_in=updatedUser)
        finally:
            return user

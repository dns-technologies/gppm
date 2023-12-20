from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from .auth_base import BaseAuth
import app.crud as crud


class DatabaseAuth(BaseAuth):
    def auth(self, email: str, password: str, *, db: Session) -> Optional[User]:
        user = crud.user.authenticate(
            db, email=email, password=password
        )

        if not user:
            user = crud.user.get_by_email(db, email=email)
            if user:
                # Пользователь существует, но пароль введен неверный
                return None

        payload = {
            "email": email,
            "password": password,
        }

        return self.update_db(payload, db=db)

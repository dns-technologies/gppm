from sqlalchemy.orm import Session
import app.crud as crud
import app.schemas as schemas
from app.core.config import settings
from app.db import base  # noqa: F401


def init_db(db: Session) -> None:
    # Таблицы должны быть созданы миграциями Alembic
    # Но, если вы не ходите использовать миграции, раскомментируйте строку ниже
    # Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841

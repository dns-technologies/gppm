from typing import Any, Dict, Optional, Union
from pydantic import PostgresDsn
from urllib.parse import unquote

from sqlalchemy.pool import NullPool
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app.core.security import encrypt_message, decrypt_message
from app.crud.crud_base import CRUDBase
from app.models.context import Context
from app.schemas.context import ContextCreate, ContextUpdate, ContextMini


class CRUDUContext(CRUDBase[Context, ContextCreate, ContextUpdate]):
    def get_by_alias(self, db: Session, *, alias: str) -> Optional[Context]:
        return db.query(Context).filter(Context.alias == alias).first()

    def create(self, db: Session, *, obj_in: ContextCreate) -> Context:
        db_obj = Context(
            alias=obj_in.alias,
            server=obj_in.server,
            port=obj_in.port,
            role=obj_in.role,
            database=obj_in.database,
            encoded_password=encrypt_message(obj_in.password),
            is_active=obj_in.is_active,
        )
        return super().create(db, obj_in=db_obj)

    def update(
        self, db: Session, *, db_obj: Context, obj_in: Union[ContextUpdate, Dict[str, Any]]
    ) -> Context:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:  # Need to check for password key
            encoded_password = encrypt_message(update_data["password"])
            del update_data["password"]
            update_data["encoded_password"] = encoded_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove(
        self, db: Session, *, db_obj: Context
    ) -> Context:
        return super().remove(db, id=db_obj.id)

    def is_active(self, context: Context) -> bool:
        return context.is_active

    def validate(self, db: Session, *, obj_in: ContextMini, connect_timeout=5) -> bool:
        result = False

        password = obj_in.password
        if password is None and obj_in.alias is not None:
            context = self.get_by_alias(db, alias=obj_in.alias)
            if context is not None:
                password = decrypt_message(context.encoded_password)

        if password is None:
            return result

        url = unquote(
            PostgresDsn.build(
                scheme="postgresql",
                user=obj_in.role,
                password=password,
                host=obj_in.server,
                port=f"{obj_in.port}",
                path=f"/{obj_in.database}",
            )
        )

        engine = create_engine(
            url,
            pool_pre_ping=True,
            poolclass=NullPool,
            connect_args={
                'connect_timeout': connect_timeout
            }
        )

        try:
            with engine.connect():
                result = True
        finally:
            return result


context = CRUDUContext(Context)

from urllib.parse import unquote
from typing import Optional
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.security import decrypt_message
from app.models.context import Context
from app.db.orm_types import GreenPlumConnection, GreenPlumEngine, GreenPlumSession


class GreenPlumConnectionsMaker():
    _engine: GreenPlumEngine

    def __init__(self, context: Context, database: Optional[str] = None):
        # Кодирование пробелов не требуется
        url = unquote(
            PostgresDsn.build(
                scheme="postgresql",
                user=context.role,
                password=decrypt_message(context.encoded_password),
                host=context.server,
                port=f'{context.port}',
                path=f'/{database or context.database}',
            )
        )

        self._engine = create_engine(
            url,
            pool_pre_ping=False,
            poolclass=NullPool,
            connect_args={
                'connect_timeout': 5,
            }
        )

    def connection(self) -> GreenPlumConnection:
        return self._engine.connect()

    def session(self) -> GreenPlumSession:
        gp_session = sessionmaker(autocommit=True, autoflush=False, bind=self._engine)
        return gp_session()

    def __del__(self):
        if hasattr(self, '_engine'):
            self._engine.dispose()

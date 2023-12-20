from typing import Iterator, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

import app.crud as crud
import app.models as models
import app.schemas as schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.greenplum import GreenPlumConnectionsMaker
from app.db.orm_types import GreenPlumConnection, GreenPlumSession
from app.core.auth import BaseAuth, get_auth_class

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


def get_auth() -> BaseAuth:
    return get_auth_class(settings.AUTH_PROVIDER)


def public_app_info() -> schemas.MsgPublicAppInfo:
    return schemas.MsgPublicAppInfo(
        api_version=settings.API_V1_STR,
        project_name=settings.PROJECT_NAME,
        auth_type=settings.AUTH_PROVIDER,
    )


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_active_context(
    ctx: int,
    db: Session = Depends(get_db)
) -> models.Context:
    context = crud.context.get(db, id=ctx)
    if not context:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Context not found")
    if not crud.context.is_active(context):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Inactive context")
    return context


def get_current_active_access(
    current_user: models.User = Depends(get_current_active_user),
    current_context: models.Context = Depends(get_current_active_context)
) -> List[models.Access]:
    accesses: List[models.Access] = current_user.accesses
    current_access = list(filter(
        lambda x:
        x.is_active and x.context_id == current_context.id,
        accesses
    ))
    return current_access


def get_greenplum(
    db: Optional[str] = None,
    context: models.Context = Depends(get_current_active_context)
) -> GreenPlumConnectionsMaker:
    return GreenPlumConnectionsMaker(context, db)


def get_greenplum_connection(
    gp: GreenPlumConnectionsMaker = Depends(get_greenplum)
) -> Iterator[GreenPlumConnection]:
    connection = gp.connection()
    try:
        yield connection
    finally:
        connection.close()


def get_greenplum_session(
    gp: GreenPlumConnectionsMaker = Depends(get_greenplum)
) -> Iterator[GreenPlumSession]:
    session = gp.session()
    try:
        yield session
    finally:
        session.close()

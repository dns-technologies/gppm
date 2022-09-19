from typing import Optional
from pydantic import BaseModel


# Shared mini properties
class ContextMiniBase(BaseModel):
    alias: Optional[str] = None
    server: str
    port: Optional[int] = 5432
    role: str
    database: Optional[str] = "template1"


class ContextMiniInDBBase(ContextMiniBase):
    class Config:
        orm_mode = True


# Shared properties
class ContextBase(ContextMiniBase):
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class ContextCreate(ContextBase):
    alias: str
    password: str


# Properties to receive via API on update
class ContextUpdate(ContextBase):
    password: Optional[str] = None


class ContextInDBBase(ContextBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Context(ContextInDBBase):
    pass


# Additional properties to return via API
class ContextMini(ContextMiniInDBBase):
    password: Optional[str]


# Additional properties stored in DB
class ContextInDB(ContextInDBBase):
    hashed_password: str

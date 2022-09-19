from typing import Optional
from pydantic import BaseModel


class RoleBase(BaseModel):
    rolname: str
    rolsuper: bool
    rolcreaterole: bool
    rolcreatedb: bool
    rolinherit: bool
    rolcanlogin: bool


class RoleCreate(RoleBase):
    password: str


class RoleUpdate(RoleBase):
    password: Optional[str] = None


class RoleInDBBase(RoleBase):
    class Config:
        orm_mode = True


class Role(RoleInDBBase):
    oid: int

from typing import List
from pydantic import BaseModel


class PrivilegeBase(BaseModel):
    pass


class PrivilegeInDBBase(PrivilegeBase):
    class Config:
        orm_mode = True


class Privilege(PrivilegeInDBBase):
    grantee: str
    grantor: str
    privs: List[str]
    privswgo: List[str]

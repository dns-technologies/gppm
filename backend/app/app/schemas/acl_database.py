from typing import List
from pydantic import BaseModel


class DatabaseBase(BaseModel):
    pass


class DatabaseInDBBase(DatabaseBase):
    class Config:
        orm_mode = True


class Database(DatabaseInDBBase):
    oid: int
    name: str
    owner: str
    acl: List[str]

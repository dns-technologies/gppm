from typing import List
from pydantic import BaseModel


class SchemaBase(BaseModel):
    pass


class SchemaInDBBase(SchemaBase):
    class Config:
        orm_mode = True


class Schema(SchemaInDBBase):
    oid: int
    name: str
    owner: str
    acl: List[str]

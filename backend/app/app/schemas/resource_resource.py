from typing import List
from pydantic import BaseModel


class ResourceGroupBase(BaseModel):
    concurrency: int
    cpu_rate_limit: int
    memory_limit: int
    group_members: List[str]


class ResourceGroupInDBBase(ResourceGroupBase):
    class Config:
        orm_mode = True


class ResourceGroup(ResourceGroupInDBBase):
    oid: int
    name: str


class ResourceGroupCreate(ResourceGroupInDBBase):
    name: str


class ResourceGroupUpdate(ResourceGroupInDBBase):
    pass

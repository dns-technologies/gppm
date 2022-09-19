from typing import List
from pydantic import BaseModel


class RoleGraphBase(BaseModel):
    pass


class RoleGraphInDBBase(RoleGraphBase):
    class Config:
        orm_mode = True


class RoleGraphItemBase(BaseModel):
    pass


class RoleGrapItemInDBBase(RoleGraphItemBase):
    class Config:
        orm_mode = True


class RoleGraphEdge(RoleGrapItemInDBBase):
    from_oid: int
    to_oid: int


class RoleGraphNode(RoleGrapItemInDBBase):
    oid: int
    rolname: str


class RoleGraph(RoleGraphInDBBase):
    nodes: List[RoleGraphNode]
    edges: List[RoleGraphEdge]

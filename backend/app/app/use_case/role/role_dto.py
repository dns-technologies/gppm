from typing import List, Optional
from attrs import define


@define
class DTO:
    pass


@define
class RoleDTO(DTO):
    oid: int
    rolname: str
    rolsuper: bool
    rolcreaterole: bool
    rolcreatedb: bool
    rolinherit: bool
    rolcanlogin: bool


@define
class RoleCreateDTO(DTO):
    rolname: str
    password: str
    rolsuper: bool
    rolcreaterole: bool
    rolcreatedb: bool
    rolinherit: bool
    rolcanlogin: bool


@define
class RoleUpdateDTO(DTO):
    rolname: str
    password: Optional[str]
    rolsuper: bool
    rolcreaterole: bool
    rolcreatedb: bool
    rolinherit: bool
    rolcanlogin: bool


@define
class MemberDTO(DTO):
    oid: int
    rolname: str


@define
class RoleGroupEdgeDTO(DTO):
    from_oid: int
    to_oid: int


@define
class RoleGroupNodeDTO(DTO):
    oid: int
    rolname: str


@define
class RoleGroupDTO(DTO):
    nodes: List[RoleGroupNodeDTO]
    edges: List[RoleGroupEdgeDTO]

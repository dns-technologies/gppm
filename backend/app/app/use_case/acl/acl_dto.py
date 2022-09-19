from attrs import define
from typing import List


@define
class DTO:
    pass


@define
class DatabaseAclDTO(DTO):
    oid: int
    name: str
    owner: str
    acl: List[str]

    def __attrs_post_init__(self):
        if self.acl is None:
            self.acl = [
                f'"{self.owner}"=CTc/"{self.owner}"',
                f'=Tc/"{self.owner}"',  # У базы всегда есть права PUBLIC
            ]


@define
class SchemaAclDTO(DTO):
    oid: int
    name: str
    owner: str
    acl: List[str]

    def __attrs_post_init__(self):
        if self.acl is None:
            self.acl = [f'"{self.owner}"=UC/"{self.owner}"']


@define
class TableAclDTO(DTO):
    oid: int
    name: str
    owner: str
    acl: List[str]
    schema: str

    def __attrs_post_init__(self):
        if self.acl is None:
            self.acl = [f'"{self.owner}"=arwdDxt/"{self.owner}"']

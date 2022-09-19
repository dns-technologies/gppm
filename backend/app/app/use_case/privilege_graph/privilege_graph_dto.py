from attrs import define
from typing import List, Optional


@define
class DTO:
    pass


@define
class PrivilegeDTO(DTO):
    grantee: str
    grantor: str
    privs: List[str]
    privswgo: List[str]


@define
class DefaultPermissonsDTO(DTO):
    schema: Optional[str]
    objtype: str
    defaclacl: List[PrivilegeDTO]


@define
class GraphPermissionsDTO(DTO):
    database: str
    db_schema: Optional[str]
    table: Optional[str]


@define
class RevokeAllDefaultsDTO(DTO):
    database: str
    db_schema: Optional[str]
    entrie_type: str
    target_role: str
    role_specification: str

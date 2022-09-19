from attrs import define
from typing import List


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
class GrantDTO(DTO):
    role_specification: str
    with_grant_option: bool


@define
class GrantDatabasePrivelegesDTO(DTO):
    create: bool
    temporary: bool
    connect: bool


@define
class GrantDatabaseDTO(GrantDTO):
    name: str
    privileges: GrantDatabasePrivelegesDTO


@define
class GrantSchemaPrivelegesDTO(DTO):
    create: bool
    usage: bool


@define
class GrantSchemasInDatabaseDTO(GrantDTO):
    database: str
    privileges: GrantSchemaPrivelegesDTO


@define
class GrantSchemaDTO(GrantDTO):
    name: str
    database: str
    privileges: GrantSchemaPrivelegesDTO


@define
class GrantTablePrivelegesDTO(DTO):
    select: bool
    insert: bool
    update: bool
    delete: bool
    truncate: bool
    references: bool
    trigger: bool


@define
class GrantTablesInDatabaseDTO(GrantDTO):
    database: str
    privileges: GrantTablePrivelegesDTO


@define
class GrantTablesInSchemaDTO(GrantDTO):
    database: str
    db_schema: str
    privileges: GrantTablePrivelegesDTO


@define
class GrantTableDTO(GrantDTO):
    name: str
    database: str
    db_schema: str
    privileges: GrantTablePrivelegesDTO

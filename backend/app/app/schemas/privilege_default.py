from typing import List, Optional
from pydantic import BaseModel
from .privilege_privilege import Privilege

class DefaultPermissionsBase(BaseModel):
    pass


class DefaultPermissionsInDBBase(DefaultPermissionsBase):
    class Config:
        orm_mode = True


class DefaultPermissions(DefaultPermissionsInDBBase):
    db_schema: Optional[str]
    objtype: str
    defaclacl: List[Privilege]

    class Config:
        allow_population_by_alias = True
        fields = {'db_schema': {'alias': 'schema'}}


class RevokeAllDefaults(DefaultPermissionsInDBBase):
    database: str
    db_schema: Optional[str]
    entrie_type: str
    target_role: str
    role_specification: str

    class Config:
        allow_population_by_alias = True
        fields = {'db_schema': {'alias': 'schema'}}
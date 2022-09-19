from typing import Optional
from pydantic import BaseModel


class GraphPermissionsBase(BaseModel):
    pass


class GraphPermissionsInDBBase(GraphPermissionsBase):
    class Config:
        orm_mode = True


class GraphPermissions(GraphPermissionsInDBBase):
    database: str
    db_schema: Optional[str]
    table: Optional[str]

    class Config:
        allow_population_by_alias = True
        fields = {'db_schema': {'alias': 'schema'}}

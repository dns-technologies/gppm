from typing import Optional
from pydantic import BaseModel


class OwnerEntityBase(BaseModel):
    pass


class OwnerEntityInDBBase(OwnerEntityBase):
    class Config:
        orm_mode = True


class OwnerEntityUpdate(OwnerEntityInDBBase):
    type_of_entity: str
    owner: str
    database: str
    db_schema: Optional[str]
    table: Optional[str]

    class Config:
        allow_population_by_alias = True
        fields = {'db_schema': {'alias': 'schema'}}

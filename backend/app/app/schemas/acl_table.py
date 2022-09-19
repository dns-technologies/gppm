from typing import List
from pydantic import BaseModel


class TableBase(BaseModel):
    pass


class TableInDBBase(TableBase):
    class Config:
        orm_mode = True


class Table(TableInDBBase):
    oid: int
    name: str
    owner: str
    acl: List[str]
    db_schema: str

    class Config:
        allow_population_by_alias = True
        fields = {'db_schema': {'alias': 'schema'}}
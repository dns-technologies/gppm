from pydantic import BaseModel


class GrantBase(BaseModel):
    role_specification: str
    with_grant_option: bool


class GrantInDBBase(GrantBase):
    class Config:
        orm_mode = True


class GrantDatabasePriveleges(BaseModel):
    create: bool
    temporary: bool
    connect: bool


class GrantDatabase(GrantInDBBase):
    name: str
    privileges: GrantDatabasePriveleges


class GrantSchemaPriveleges(BaseModel):
    create: bool
    usage: bool


class GrantSchemasInDatabase(GrantInDBBase):
    database: str
    privileges: GrantSchemaPriveleges


class GrantSchema(GrantInDBBase):
    name: str
    database: str
    privileges: GrantSchemaPriveleges


class GrantTablePriveleges(BaseModel):
    select: bool
    insert: bool
    update: bool
    delete: bool
    truncate: bool
    references: bool
    trigger: bool


class GrantTablesInDatabase(GrantInDBBase):
    database: str
    privileges: GrantTablePriveleges


class GrantTablesInSchema(GrantInDBBase):
    database: str
    db_schema: str
    privileges: GrantTablePriveleges

    class Config:
        allow_population_by_alias = True
        fields = {'db_schema': {'alias': 'schema'}}


class GrantTable(GrantInDBBase):
    name: str
    database: str
    db_schema: str
    privileges: GrantTablePriveleges

    class Config:
        allow_population_by_alias = True
        fields = {'db_schema': {'alias': 'schema'}}

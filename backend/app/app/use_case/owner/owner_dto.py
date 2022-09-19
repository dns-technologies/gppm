from attr import field
from attrs import define
from typing import Optional


@define
class DTO:
    pass


@define
class UpdateOwnerDTO(DTO):
    type_of_entity: str = field()
    owner: str
    database: str
    db_schema: Optional[str]
    table: Optional[str]

    @type_of_entity.validator
    def check(self, attribute, value):
        if value not in ('database', 'schema', 'table'):
            raise ValueError("Field type_of_entity has an invalid value")

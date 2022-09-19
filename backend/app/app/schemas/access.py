from typing import Optional
from pydantic import BaseModel, validator


# Shared properties
class AccessBase(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
    database: Optional[str] = None
    db_schema: Optional[str] = None
    is_active: Optional[bool] = True
    context_id: Optional[int] = None


# Properties to receive via API on creation
class AccessCreate(AccessBase):
    user_id: int
    context_id: int


# Properties to receive via API on update
class AccessUpdate(AccessBase):
    pass


class AccessInDBBase(AccessBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Access(AccessInDBBase):
    type_of_entity: Optional[str] = None

    @validator("type_of_entity", always=True)
    def type_of_entity_compute(cls, v, values, **kwargs) -> str:
        all_fields = (
            bool(values["role"]),
            bool(values["database"]),
            bool(values["db_schema"])
        )

        all_types = {
            (True, False, False): "Role",
            (False, True, False): "Database",
            (False, True, True): "Schema",
        }

        final_type = all_types.get(all_fields)
        if final_type is not None:
            return final_type
            
        return "Nothing"


# Additional properties stored in DB
class AccessInDB(AccessInDBBase):
    pass

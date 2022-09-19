from pydantic import BaseModel


class RoleMemberBase(BaseModel):
    pass


class RoleMemberInDBBase(RoleMemberBase):
    class Config:
        orm_mode = True


class RoleMember(RoleMemberInDBBase):
    oid: int
    rolname: str

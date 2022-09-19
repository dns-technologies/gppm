from pydantic import BaseModel


class Msg(BaseModel):
    msg: str


class MsgPublicAppInfo(BaseModel):
    project_name: str
    api_version: str
    auth_type: str

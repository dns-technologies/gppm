from typing import List
from pydantic import BaseModel


class ACLRule(BaseModel):
    acls: List[str]

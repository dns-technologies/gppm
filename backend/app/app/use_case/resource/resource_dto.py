from typing import List
from attrs import define, field


def null2list(x) -> list:
    if x == [None]:
        return []

    return x


@define
class DTO:
    pass


@define
class ResourceGroupDTO(DTO):
    oid: int
    name: str
    concurrency: int
    cpu_rate_limit: int
    memory_limit: int
    group_members: List[str] = field(converter=null2list)


@define
class ResourceGroupCreateDTO(DTO):
    name: str
    concurrency: int
    cpu_rate_limit: int
    memory_limit: int
    group_members: List[str] = field(converter=null2list)


@define
class ResourceGroupUpdateDTO(DTO):
    concurrency: int
    cpu_rate_limit: int
    memory_limit: int
    group_members: List[str] = field(converter=null2list)


@define
class ResourceGroupAvailableLimitsDTO(DTO):
    cpu_rate_limit_min: int
    cpu_rate_limit_max: int
    memory_limit_min: int
    memory_limit_max: int
    concurrency_min: int
    concurrency_max: int

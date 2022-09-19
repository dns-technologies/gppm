from pydantic import BaseModel


class ResourceGroupLimitsBase(BaseModel):
    pass


class ResourceGroupLimitsInDBBase(ResourceGroupLimitsBase):
    class Config:
        orm_mode = True


class ResourceGroupAvailableLimits(ResourceGroupLimitsInDBBase):
    concurrency_min: int
    cpu_rate_limit_min: int
    memory_limit_min: int
    concurrency_max: int
    cpu_rate_limit_max: int
    memory_limit_max: int

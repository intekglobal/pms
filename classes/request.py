from pydantic import BaseModel
from typing import Literal


class LocalParams(BaseModel):
    location_id: str
    tenant_id: str


class NexHealthParams(BaseModel):
    location_id: int
    subdomain: str


class RequestConfiguration(BaseModel):
    type: Literal["Local", "NexHealth"]
    params: NexHealthParams | LocalParams


class Request(BaseModel):
    configuration: RequestConfiguration

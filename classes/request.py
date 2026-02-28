from pydantic import BaseModel
from typing import Literal
from typing import Sequence

# Local packages
from .nexhealth import NexHealthAppointment
from .nexhealth import NexHealthPatient
from .pms import PMSPatient


class GetPatientsResponse(BaseModel):
    count: int
    data: Sequence[PMSPatient] | Sequence[NexHealthPatient]


class LocalParams(BaseModel):
    location_id: str
    tenant_id: str


class NexHealthGetAppointmentsResponse(BaseModel):
    count: int
    data: Sequence[NexHealthAppointment]


class NexHealthGetPatientsResponse(BaseModel):
    count: int
    data: Sequence[NexHealthPatient]


class NexHealthParams(BaseModel):
    email: str
    location_id: int
    operatory_id: int
    provider_id: int
    subdomain: str


class RequestConfiguration(BaseModel):
    type: Literal["Local", "NexHealth"]
    params: NexHealthParams | LocalParams

from pydantic import BaseModel
from typing import Literal
from typing import Sequence

# Local packages
from .nexhealth import NexHealthAppointment
from .nexhealth import NexHealthPatient
from .pms import Appointment
from .pms import Patient


class GetAppointmentsResponse(BaseModel):
    count: int
    data: Sequence[Appointment | NexHealthAppointment]


class GetPatientsResponse(BaseModel):
    count: int
    data: Sequence[Patient] | Sequence[NexHealthPatient]


class LocalParams(BaseModel):
    location_id: str
    tenant_id: str


class NexHealthParams(BaseModel):
    default_patient_email: str | None = None
    default_provider_id: int | None = None
    location_id: int
    subdomain: str


class RequestConfiguration[T = LocalParams | NexHealthParams](BaseModel):
    type: Literal["Local", "NexHealth"]
    params: T

from pydantic import BaseModel
from typing import Literal
from typing import Sequence

# Local imports
from classes.nexhealth import NexHealthAppointment
from classes.nexhealth import NexHealthAppointmentSlotResponse
from classes.nexhealth import NexHealthAvailability
from classes.nexhealth import NexHealthLocationResponse
from classes.nexhealth import NexHealthOperatory
from classes.nexhealth import NexHealthPatient
from classes.nexhealth import NexHealthProvider
from classes.pms import Appointment
from classes.pms import Patient


class GetResponse[D](BaseModel):
    count: int
    data: D


class GetAppointmentSlotsResponse(
    GetResponse[Sequence[NexHealthAppointmentSlotResponse]]
):
    count: int


class GetAppointmentsResponse(BaseModel):
    count: int
    data: Sequence[Appointment] | Sequence[NexHealthAppointment]


class GetAvailabilitiesResponse(GetResponse[Sequence[NexHealthAvailability]]):
    count: int


class GetLocationsResponse(GetResponse[Sequence[NexHealthLocationResponse]]):
    count: int


class GetOperatoriesResponse(GetResponse[Sequence[NexHealthOperatory]]):
    count: int


class GetPatientsResponse(BaseModel):
    count: int
    data: Sequence[Patient] | Sequence[NexHealthPatient]


class GetProvidersResponse(GetResponse[Sequence[NexHealthProvider]]):
    count: int


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

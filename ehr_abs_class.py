from abc import ABCMeta
from abc import abstractmethod
from pydantic import BaseModel
from typing import Literal
from typing import Sequence
from typing import TypedDict

PER_PAGE = 300


class PMSPatient(BaseModel):
    date_of_birth: str
    first_name: str
    home_phone: str
    last_name: str
    patient_number: int
    patient_status: Literal["Prospective", "Patient"]
    phone_number: str
    primary_provider: int
    wireless_phone: str
    work_phone: str


class GetPatientsResponse(TypedDict):
    count: int
    data: Sequence[PMSPatient]


class LocalConfig(BaseModel):
    location_id: str
    tenant_id: str


class NexHealthConfig(BaseModel):
    location_id: int
    subdomain: str


class PMSAbstractBaseClass(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_patients(
        cls,
        *,
        configuration: NexHealthConfig | LocalConfig,
        date_of_birth: str | None = None,
        # location_id: str,
        per_page: int = PER_PAGE,
        phone_number: int | str | None = None,
        # tenant_id: str,
    ) -> GetPatientsResponse:
        # ) -> Sequence[PMSPatient]:
        return {
            "count": 0,
            "data": [],
        }

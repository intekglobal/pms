from abc import ABCMeta
from abc import abstractmethod
from pydantic import BaseModel
from typing import Literal
from typing import Sequence

# Local imports
from classes.request import LocalParams
from classes.request import NexHealthParams

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


class GetPatientsResponse(BaseModel):
    count: int
    data: Sequence[PMSPatient]


type LocalConfig = LocalParams
type NexHealthConfig = NexHealthParams


class PMSAbstractBaseClass(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_patients(
        cls,
        *,
        configuration: NexHealthConfig | LocalConfig,
        date_of_birth: str | None = None,
        per_page: int = PER_PAGE,
        phone_number: str | None = None,
    ) -> GetPatientsResponse:
        return GetPatientsResponse(
            count=0,
            data=[],
        )

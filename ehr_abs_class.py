import datetime as dt
from abc import ABCMeta
from abc import abstractmethod

# Local imports
from classes.request import GetPatientsResponse
from classes.request import LocalParams
from classes.request import NexHealthParams

PER_PAGE = 300


type LocalConfig = LocalParams
type NexHealthConfig = NexHealthParams


class PMSAbstractBaseClass[C = LocalConfig | NexHealthConfig](metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def get_patients(
        cls,
        *,
        configuration: C,
        date_of_birth: dt.date | None = None,
        per_page: int = PER_PAGE,
        phone_number: str | None = None,
    ) -> GetPatientsResponse:
        return GetPatientsResponse(
            count=0,
            data=[],
        )

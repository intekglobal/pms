from pydantic import BaseModel
from typing import Literal


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

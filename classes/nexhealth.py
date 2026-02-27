from pydantic import BaseModel
from typing import Literal
from typing import Sequence


class Bio(BaseModel):
    city: str = ""
    state: str = ""
    gender: Literal["Female", "Male"] | None = "Female"
    zip_code: int | None = None
    new_patient: bool
    phone_number: str
    date_of_birth: str
    address_line_1: str = ""
    address_line_2: str = ""
    street_address: str = ""
    cell_phone_number: str = ""
    home_phone_number: str = ""
    work_phone_number: str = ""
    previous_foreign_id: str | None = None


class NexHealthAppointment(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    provider_name: str
    start_time: str
    confirmed: bool
    patient_missed: bool
    created_at: str
    updated_at: str
    note: str
    end_time: str
    unavailable: bool
    cancelled: bool
    timezone: str
    institution_id: int
    location_id: int
    foreign_id: str
    foreign_id_type: str
    patient_confirmed: bool
    created_by_user_id: int | None
    is_guardian: bool
    operatory_id: int
    timezone_offset: str


class NexHealthPatient(BaseModel):
    id: int
    email: str | None
    first_name: str
    middle_name: str | None = None
    last_name: str
    name: str
    created_at: str
    updated_at: str
    institution_id: int
    foreign_id: str | None
    foreign_id_type: str | Literal["nex"]
    bio: Bio
    inactive: bool
    last_sync_time: str | None
    preferred_language: str | None
    location_ids: Sequence[int]
    provider_id: int

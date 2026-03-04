from typing import Literal
from typing import NotRequired
from typing import Sequence
from typing import TypedDict


class Bio(TypedDict):
    city: NotRequired[str]
    state: NotRequired[str]
    gender: NotRequired[Literal["Female", "Male"] | None]
    zip_code: NotRequired[int | None]
    new_patient: bool
    phone_number: str
    date_of_birth: str
    address_line_1: NotRequired[str]
    address_line_2: NotRequired[str]
    street_address: NotRequired[str]
    cell_phone_number: NotRequired[str]
    home_phone_number: NotRequired[str]
    work_phone_number: NotRequired[str]
    previous_foreign_id: NotRequired[str | None]


class NexHealthAppointment(TypedDict):
    id: int
    patient_id: int
    provider_id: int
    provider_name: str
    start_time: str
    confirmed: bool
    patient_missed: bool
    created_at: str
    updated_at: str
    note: str | None
    end_time: str
    unavailable: bool
    cancelled: bool
    cancelled_at: str | None
    timezone: str
    institution_id: int
    location_id: int
    foreign_id: str | None
    foreign_id_type: str | Literal["nex"]
    patient_confirmed: bool
    created_by_user_id: int | None
    is_guardian: bool
    operatory_id: int | None
    timezone_offset: str


class NexHealthPatient(TypedDict):
    id: int
    email: str | None
    first_name: str
    middle_name: str | None
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

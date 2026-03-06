from typing import Dict
from typing import Literal
from typing import NotRequired
from typing import Sequence
from typing import TypedDict

type NexHealthIncludeAppointmentQueryValue = Literal[
    "operatory",
    "patient",
    "procedures",
]
type NexHealthIncludePatientQueryValue = Literal[
    "adjustments",
    "upcoming_appts",
]
type NexHealthIncludeAppointmentQuery = Sequence[NexHealthIncludeAppointmentQueryValue]
type NexHealthIncludePatientQuery = Sequence[NexHealthIncludePatientQueryValue]


class BaseNexHealthAppointment(TypedDict):
    confirmed: bool
    end_time: str
    id: int
    location_id: int
    provider_id: int
    provider_name: str
    start_time: str


class Bio(TypedDict):
    city: NotRequired[str]
    state: NotRequired[str]
    gender: NotRequired[Literal["Female", "Male"] | None]
    zip_code: NotRequired[int | None]
    new_patient: bool
    non_patient: bool
    phone_number: str
    date_of_birth: str
    address_line_1: NotRequired[str]
    address_line_2: NotRequired[str]
    street_address: NotRequired[str]
    cell_phone_number: NotRequired[str]
    home_phone_number: NotRequired[str]
    work_phone_number: NotRequired[str]
    previous_foreign_id: NotRequired[str | None]


class BaseNexHealthPatient(TypedDict):
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


class NexHealthAppointment(BaseNexHealthAppointment):
    patient_id: int
    confirmed_at: str | None
    patient_missed: bool
    created_at: str
    updated_at: str
    note: str | None
    unavailable: bool
    cancelled: bool
    cancelled_at: str | None
    timezone: str
    institution_id: int
    foreign_id: str | None
    foreign_id_type: str | Literal["nex"]
    operatory: NotRequired[Dict]
    patient_confirmed: bool
    patient: NotRequired[BaseNexHealthPatient]
    procedures: NotRequired[Sequence[Dict]]
    created_by_user_id: int | None
    is_guardian: bool
    operatory_id: int | None
    timezone_offset: str


class NexHealthPatient(BaseNexHealthPatient):
    adjustments: NotRequired[Sequence[Dict]]
    provider_id: int
    upcoming_appts: NotRequired[Sequence[Dict]]


type NexHealthSubscriptionFeature = Literal[
    "campaigns",
    "enterprise",
    "forms",
    "insurance_verification",
    "ledger_sync",
    "messaging",
    "online_booking",
    "payments",
    "recalls",
    "reminders",
    "reviews",
    "waitlist",
]

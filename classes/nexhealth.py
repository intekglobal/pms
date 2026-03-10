from typing import Dict
from typing import Literal
from typing import NotRequired
from typing import Sequence
from typing import TypedDict

type NexHealthGender = Literal["Female", "Male", "Other"]
type NexHealthIncludeAppointmentQueryValue = Literal[
    "operatory",
    "patient",
    "procedures",
]
type NexHealthIncludeAppointmentQuery = Sequence[NexHealthIncludeAppointmentQueryValue]
type NexHealthIncludePatientQueryValue = Literal[
    "adjustments",
    "procedures",
    "upcoming_appts",
]
type NexHealthIncludePatientQuery = Sequence[NexHealthIncludePatientQueryValue]
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


class BaseBaseNexHealthPatient(TypedDict):
    first_name: str
    last_name: str


class BaseBio(TypedDict):
    date_of_birth: str
    gender: NotRequired[NexHealthGender | None]


class BaseNexHealthAppointment(TypedDict):
    confirmed: bool
    end_time: str
    id: int
    location_id: int
    provider_id: int
    provider_name: str
    start_time: str


class Bio(BaseBio):
    city: NotRequired[str | None]
    state: NotRequired[str | None]
    zip_code: NotRequired[int | None]
    new_patient: bool
    non_patient: bool
    phone_number: str
    address_line_1: NotRequired[str | None]
    address_line_2: NotRequired[str | None]
    street_address: NotRequired[str | None]
    cell_phone_number: NotRequired[str | None]
    home_phone_number: NotRequired[str | None]
    work_phone_number: NotRequired[str | None]
    previous_foreign_id: NotRequired[str | None]


class BaseNexHealthPatient(BaseBaseNexHealthPatient):
    id: int
    email: str | None
    middle_name: str | None
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
    operatory: NotRequired[Dict | None]
    patient_confirmed: bool
    patient: NotRequired[BaseNexHealthPatient | None]
    procedures: NotRequired[Sequence[Dict] | None]
    created_by_user_id: int | None
    is_guardian: bool
    operatory_id: int | None
    timezone_offset: str


class NexHealthGuardianPatient(BaseBaseNexHealthPatient):
    bio: BaseBio


class NexHealthPatient(BaseNexHealthPatient):
    adjustments: NotRequired[Sequence[Dict] | None]
    procedures: NotRequired[Sequence[Dict] | None]
    provider_id: int
    upcoming_appts: NotRequired[Sequence[BaseNexHealthAppointment] | None]

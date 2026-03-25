from typing import Dict
from typing import Literal
from typing import NotRequired
from typing import Sequence
from typing import TypedDict

# Local imports
from type_definitions.miscellaneous_types import DayType
from type_definitions.miscellaneous_types import GenderType


class BaseBaseNexHealthPatient(TypedDict):
    first_name: str
    last_name: str


class BaseNexHealthAppointment(TypedDict):
    confirmed: bool
    end_time: str
    id: int
    location_id: int
    provider_id: int
    provider_name: str
    start_time: str


class BaseNexHealthBio(TypedDict):
    date_of_birth: str
    gender: NotRequired[GenderType | None]


class NexHealthProviderBio(TypedDict):
    cell_phone_number: NotRequired[str | None]
    home_phone_number: NotRequired[str | None]
    phone_number: str


class NexHealthBio(BaseNexHealthBio, NexHealthProviderBio):
    address_line_1: NotRequired[str | None]
    address_line_2: NotRequired[str | None]
    city: NotRequired[str | None]
    new_patient: bool
    non_patient: NotRequired[bool | None]
    previous_foreign_id: NotRequired[str | None]
    state: NotRequired[str | None]
    street_address: NotRequired[str | None]
    work_phone_number: NotRequired[str | None]
    zip_code: NotRequired[str | None]


class NexHealthPatientAndProviderCommonProps(BaseBaseNexHealthPatient):
    created_at: str
    email: str | None
    foreign_id: str | None
    foreign_id_type: str | Literal["nex"]
    id: int
    inactive: bool
    institution_id: int
    last_sync_time: str | None
    middle_name: str | None
    name: str
    updated_at: str


class BaseNexHealthPatient(NexHealthPatientAndProviderCommonProps):
    bio: NexHealthBio
    location_ids: Sequence[int]
    preferred_language: str | None


class NexHealthFee(TypedDict):
    amount: float
    currency: str


class NexHealthProcedure(TypedDict):
    appointment_id: int | None
    body_site: Dict | None
    code: str
    end_date: str | None
    fee: NexHealthFee | None
    id: int
    location_id: int
    name: str
    patient_id: int
    provider_id: int
    start_date: str | None
    status: str
    updated_at: str


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
    procedures: NotRequired[Sequence[NexHealthProcedure] | None]
    created_by_user_id: int | None
    is_guardian: bool
    operatory_id: int | None
    timezone_offset: str


class NexHealthAppointmentSlot(TypedDict):
    end_time: str
    operatory_id: int
    provider_id: int
    time: str


class NexHealthAppointmentSlotResponse(TypedDict):
    lid: int
    next_available_date: str
    operatory_id: int
    pid: int
    slots: Sequence[NexHealthAppointmentSlot]


class NexHealthAppointmentType(TypedDict):
    id: int
    name: str
    parent_type: Literal["Institution", "Location"]
    parent_id: int
    minutes: int
    bookable_online: bool


class NexHealthCustomRecurrence(TypedDict):
    num: int
    ref: str  # string date
    # required field, but it can be an empty string as a way to "opt out"
    unit: Literal["", "day", "month", "week"]


class NexHealthAvailability(TypedDict):
    active: bool
    appointment_types: NotRequired[Sequence[NexHealthAppointmentType]]
    begin_time: str  # HH:mm
    custom_recurrence: NexHealthCustomRecurrence | None
    days: Sequence[DayType]
    end_time: str  # HH:mm
    id: int
    location_id: int
    operatory_id: int
    provider_id: int
    specific_date: str | None
    synced: bool
    tz_offset: str


class NexHealthGuardianPatient(BaseBaseNexHealthPatient):
    bio: BaseNexHealthBio


class NexHealthLocation(TypedDict):
    appt_types_map_by_operatory: bool
    city: str
    country_code: str
    created_at: str
    email: str | None
    foreign_id: str
    foreign_id_type: str
    id: int
    inactive: bool
    insert_appt_client: bool
    institution_id: int
    last_sync_time: str | None
    latitude: float  # can be negative
    longitude: float  # can be negative
    map_by_operatory: bool
    name: str
    phone_number: str
    set_availability_by_operatory: bool
    state: str | None
    street_address: str
    street_address_2: str
    tz: str
    updated_at: str
    weight: int | None
    wlogo: str
    zip_code: str


class NexHealthLocationResponse(TypedDict):
    id: int
    locations: Sequence[NexHealthLocation]
    name: str
    subdomain: str


class NexHealthOperatory(TypedDict):
    active: bool
    appt_categories: Sequence[Dict]
    bookable_online: bool
    created_at: str
    display_name: str | None
    foreign_id: str
    foreign_id_type: str
    id: int
    last_sync_time: str | None
    location_id: int
    name: str
    profile_url: str
    updated_at: str


class NexHealthPatient(BaseNexHealthPatient):
    adjustments: NotRequired[Sequence[Dict] | None]
    appointments: NotRequired[Sequence[BaseNexHealthAppointment] | None]
    procedures: NotRequired[Sequence[NexHealthProcedure] | None]
    # When a patient record has no provider ID, it's highly likely that it is corrupted.
    provider_id: int | None
    upcoming_appts: NotRequired[Sequence[BaseNexHealthAppointment] | None]


class NexHealthProviderRequestable(TypedDict):
    location_id: int


class NexHealthProvider(NexHealthPatientAndProviderCommonProps):
    availabilities: NotRequired[Sequence[NexHealthAvailability] | None]
    bio: NexHealthProviderBio
    display_name: str | None
    locations: NotRequired[Sequence[NexHealthLocation] | None]
    npi: str | None
    provider_requestables: Sequence[NexHealthProviderRequestable]
    specialty_code: str
    state_license: str | None
    tin: str | None

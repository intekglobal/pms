from pydantic import BaseModel
from typing import Literal
from typing import Sequence


class Bio(BaseModel):
    city: str = ""
    state: str = ""
    gender: Literal["Female", "Male"] | None = "Female"
    zip_code: int | None = None
    new_patient: bool
    # non_patient: bool
    phone_number: str
    date_of_birth: str
    address_line_1: str = ""
    address_line_2: str = ""
    street_address: str = ""
    cell_phone_number: str = ""
    home_phone_number: str = ""
    work_phone_number: str = ""
    previous_foreign_id: str | None = None


class NexHealthPatient(BaseModel):
    id: int
    email: str | None = None
    first_name: str
    middle_name: str | None = None
    last_name: str
    name: str
    created_at: str
    updated_at: str
    # institution_id: int
    # foreign_id: int | None = None
    # foreign_id_type: Literal['nex'] | str
    bio: Bio
    inactive: bool
    last_sync_time: str
    # guarantor_id: str | None = None
    # unsubscribe_sms: bool
    # balance: {
    #     "amount": "0.00",
    #     "currency": "USD"
    # }
    # billing_type: str
    # # billing_type: "Standard"
    # chart_id: str | None = None
    # preferred_language: str
    # # preferred_language: "en"
    # preferred_locale: str | None = None
    location_ids: Sequence[int]
    provider_id: int

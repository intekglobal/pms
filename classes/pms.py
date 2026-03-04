from pydantic import AliasPath
from pydantic import BaseModel
from pydantic import Field
from typing import Dict
from typing import Sequence

# Local imports
from classes.nexhealth import NexHealthProcedure


class BaseAppointment(BaseModel):
    """
    Provides the basic properties necessary to represent an appointment object,
    used when wither only this information is required of when showing the complete
    list of properties(by extending it).
    """

    confirmed: bool
    end_time: str
    id: int
    location_id: int
    provider_id: int
    provider_name: str
    start_time: str


class BasePatient(BaseModel):
    """
    Patient minimum required properties; used when working with basic `Patient` objects
    or when the complete list of properties is shown by extending it.
    """

    date_of_birth: str = Field(
        validation_alias=AliasPath("bio", "date_of_birth"),
    )
    first_name: str
    home_phone: str | None = Field(
        default=None,
        validation_alias=AliasPath("bio", "home_phone_number"),
    )
    id: int
    last_name: str
    new_patient: bool
    phone_number: str = Field(
        validation_alias=AliasPath("bio", "phone_number"),
    )
    wireless_phone: str | None = Field(
        default=None,
        validation_alias=AliasPath("bio", "cell_phone_number"),
    )
    work_phone: str | None = Field(
        default=None,
        validation_alias=AliasPath("bio", "work_phone_number"),
    )


class Appointment(BaseAppointment):
    """
    Representation of an appointment request/record.
    """

    cancelled: bool
    note: str | None = None
    operatory: Dict | None = None
    operatory_id: int | None
    patient: BasePatient | None
    patient_id: int
    procedures: Sequence[NexHealthProcedure] | None = None
    provider_id: int


class Patient(BasePatient):
    """
    Representation of a patient.
    """

    adjustments: Sequence[Dict] | None = None
    procedures: Sequence[NexHealthProcedure] | None = None
    provider_id: int
    upcoming_appointments: Sequence[BaseAppointment] | None = Field(
        default=None,
        validation_alias=AliasPath("upcoming_appts"),
    )

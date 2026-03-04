from pydantic import AliasPath
from pydantic import BaseModel
from pydantic import Field


class Patient(BaseModel):
    """
    Representation of a patient.
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
    provider_id: int
    wireless_phone: str | None = Field(
        default=None,
        validation_alias=AliasPath("bio", "cell_phone_number"),
    )
    work_phone: str = Field(
        default=None,
        validation_alias=AliasPath("bio", "work_phone_number"),
    )

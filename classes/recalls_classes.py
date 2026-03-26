from pydantic import BaseModel
from .pms import Patient


class RecallsPatientProviderInfo(BaseModel):
    """
    This is the provider's info used to create the recall, which can be either the
    patient's next appointment provider, or the info of the provider configured for
    the patient if there are no upcoming appointments booked.
    """

    provider_id: int
    provider_name: str
    # Whether the provider's info is from an upcoming appointment
    upcoming_appointment: bool = False


class RecallsPatient(Patient):
    """
    A patient class used specifically for *Recalls*, it is exactly like `Patient`
    except for it provides an additional field `provider_name`.
    """

    recall_provider_info: RecallsPatientProviderInfo

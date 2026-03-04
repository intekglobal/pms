from typing import Sequence

# Local packages
from classes.nexhealth import NexHealthPatient
from classes.pms import Patient


def generate_pms_patient(nexhealth_patient: NexHealthPatient) -> Patient:
    patient = Patient.model_validate(
        {
            "bio": nexhealth_patient["bio"],
            "first_name": nexhealth_patient["first_name"],
            "id": nexhealth_patient["id"],
            "last_name": nexhealth_patient["last_name"],
            "new_patient": nexhealth_patient["foreign_id"] is None,
            "provider_id": nexhealth_patient["provider_id"],
        }
    )
    return patient


def generate_pms_patients(data: Sequence[NexHealthPatient]):
    pms_patients = [generate_pms_patient(value) for value in data]
    return pms_patients

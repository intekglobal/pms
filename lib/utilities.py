from typing import Sequence

# Local packages
from classes.nexhealth import NexHealthPatient
from classes.pms import Patient


def generate_pms_patient(nexhealth_patient: NexHealthPatient) -> Patient:
    patient = Patient.model_validate(
        {
            **nexhealth_patient,
            "new_patient": nexhealth_patient["foreign_id"] is None,
        }
    )
    return patient


def generate_pms_patients(data: Sequence[NexHealthPatient]):
    pms_patients = [generate_pms_patient(value) for value in data]
    return pms_patients

from typing import Sequence

# Local packages
from classes.nexhealth import NexHealthPatient
from classes.pms import PMSPatient


def generate_pms_patient(nexhealth_patient: NexHealthPatient):
    patient_bio = nexhealth_patient.bio
    pms_patient = PMSPatient(
        date_of_birth=patient_bio.date_of_birth,
        first_name=nexhealth_patient.first_name,
        home_phone=patient_bio.home_phone_number,
        last_name=nexhealth_patient.last_name,
        patient_status="Prospective" if patient_bio.new_patient else "Patient",
        patient_number=nexhealth_patient.id,
        phone_number=patient_bio.phone_number,
        primary_provider=nexhealth_patient.provider_id,
        wireless_phone=patient_bio.cell_phone_number,
        work_phone=patient_bio.work_phone_number,
    )
    return pms_patient


def generate_pms_patients(data: Sequence[NexHealthPatient]):
    pms_patients = [generate_pms_patient(value) for value in data]
    return pms_patients

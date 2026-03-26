import datetime as dt
from typing import Sequence

# Local imports
from classes.nexhealth import NexHealthAppointment
from classes.nexhealth import NexHealthPatient
from classes.pms import Appointment
from classes.pms import Patient
from .pms_utilities import compute_new_patient_value


def calculate_age(date_of_birth: dt.date):
    today = dt.date.today()
    age = (
        today.year
        - date_of_birth.year
        - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    )
    return age


def generate_pms_appointment(
    nexhealth_appointment: NexHealthAppointment,
) -> Appointment:
    nexhealth_patient = (
        nexhealth_appointment["patient"] if "patient" in nexhealth_appointment else None
    )
    appointment = Appointment.model_validate(
        {
            **nexhealth_appointment,
            "patient": (
                generate_pms_patient(
                    {
                        **nexhealth_patient,
                        "provider_id": nexhealth_appointment["provider_id"],
                    }
                )
                if nexhealth_patient
                else None
            ),
        }
    )
    return appointment


def generate_pms_appointments(data: Sequence[NexHealthAppointment]):
    pms_appointments = [generate_pms_appointment(value) for value in data]
    return pms_appointments


def generate_pms_patient(nexhealth_patient: NexHealthPatient) -> Patient:
    patient = Patient.model_validate(
        {
            **nexhealth_patient,
            "new_patient": compute_new_patient_value(nexhealth_patient),
        }
    )
    return patient


def generate_pms_patients(data: Sequence[NexHealthPatient]):
    pms_patients = [generate_pms_patient(value) for value in data]
    return pms_patients

from classes.nexhealth import NexHealthPatient


def compute_new_patient_value(nexhealth_patient: NexHealthPatient) -> bool:
    new_patient = nexhealth_patient["foreign_id"] is None
    return new_patient

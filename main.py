from typing import TypedDict
from fastapi import FastAPI
from classes.nexhealth_class import NexHealthSDK
from ehr_abs_class import NexHealthConfig
from ehr_abs_class import PER_PAGE

app = FastAPI()


class CreateAppointmentData(TypedDict):
    operatory_id: int
    patient_id: int
    provider_id: int
    start_time: str


@app.post("/appointments")
async def create_appointment(
    location_id: int,
    subdomain: str,
    data: CreateAppointmentData,
):
    appointment_result = NexHealthSDK.create_appointment(
        location_id=location_id,
        operatory_id=data["operatory_id"],
        patient_id=data["operatory_id"],
        provider_id=data["provider_id"],
        start_time=data["start_time"],
        subdomain=subdomain,
    )
    return appointment_result


@app.get("/patients")
async def get_patients(
    location_id: int,
    # location_id: str,
    tenant_id: str,
    subdomain: str,
    date_of_birth: str | None = None,
    per_page: int = PER_PAGE,
    phone_number: str | None = None,
):
    patients = NexHealthSDK.get_patients(
        configuration=NexHealthConfig(
            location_id=location_id,
            subdomain=subdomain,
        ),
        date_of_birth=date_of_birth,
        per_page=per_page,
        phone_number=phone_number,
    )
    return patients

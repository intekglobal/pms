from fastapi import FastAPI
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from typing import TypedDict

# Local import
from classes.nexhealth_class import NexHealthSDK
from classes.request import NexHealthParams
from classes.request import Request
from classes.request import RequestConfiguration
from ehr_abs_class import PER_PAGE

app = FastAPI()


class CreateAppointmentData(TypedDict):
    operatory_id: int
    patient_id: int
    provider_id: int
    start_time: str


@app.post("/appointments")
async def retrieve_appointments(
    body: Request,
    end_date: str,
    start_date: str,
):
    configuration = body.configuration
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(
            HTTP_400_BAD_REQUEST, "Configuration type currently not supported"
        )

    get_appointments_response = NexHealthSDK.get_appointments(
        configuration=params,
        end=end_date,
        start=start_date,
    )
    return get_appointments_response


@app.post("/cancel_appointment/{id}")
async def cancel_appointment(body: Request, id: int):
    configuration = body.configuration
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(
            HTTP_400_BAD_REQUEST, "Configuration type currently not supported"
        )

    patch_appointment_response = NexHealthSDK.patch_appointment(
        cancel=True, configuration=params, id=id
    )
    return patch_appointment_response


@app.post("/create_appointment")
async def create_appointment(
    configuration: RequestConfiguration,
    data: CreateAppointmentData,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, "Incorrect configuration")

    appointment_result = NexHealthSDK.create_appointment(
        configuration=params,
        operatory_id=data["operatory_id"],
        patient_id=data["patient_id"],
        provider_id=data["provider_id"],
        start_time=data["start_time"],
    )
    return appointment_result


@app.post("/patients")
async def get_patients(
    body: Request,
    date_of_birth: str | None = None,
    per_page: int = PER_PAGE,
    phone_number: str | None = None,
):
    configuration = body.configuration
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, "Incorrect configuration")

    patients = NexHealthSDK.get_patients(
        configuration=params,
        date_of_birth=date_of_birth,
        per_page=per_page,
        phone_number=phone_number,
    )
    return patients

from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Annotated

# Local import
from classes.nexhealth_class import NexHealthSDK
from classes.request import NexHealthParams
from classes.request import Request
from classes.request import RequestConfiguration
from ehr_abs_class import PER_PAGE

app = FastAPI()


class CreatePatientData(BaseModel):
    date_of_birth: str
    email: str
    first_name: str
    last_name: str
    phone_number: str


@app.post("/appointments")
async def retrieve_appointments(
    body: Request,
    end_date: str,
    start_date: str,
    patient_id: int | None = None,
    per_page: int = PER_PAGE,
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
        patient_id=patient_id,
        per_page=per_page,
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
    patient_id: Annotated[int, Body()],
    start_time: Annotated[str, Body()],
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, "Incorrect configuration")

    appointment_result = NexHealthSDK.create_appointment(
        configuration=params,
        patient_id=patient_id,
        start_time=start_time,
    )
    return appointment_result


@app.post("/create_patient")
async def create_patient(configuration: RequestConfiguration, data: CreatePatientData):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, "Incorrect configuration")

    create_patient_response = NexHealthSDK.create_patient(
        configuration=params,
        date_of_birth=data.date_of_birth,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
    )
    return create_patient_response


@app.post("/patients")
async def retrieve_patients(
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


@app.post("/reschedule_appointment/{id}")
async def reschedule_appointment(
    configuration: Annotated[RequestConfiguration, Body()],
    id: int,
    start_time: Annotated[str, Body()],
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, "Incorrect configuration")

    patch_appointment_response = NexHealthSDK.patch_appointment(
        cancel=True,
        configuration=params,
        id=id,
    )
    create_appointment_response = NexHealthSDK.create_appointment(
        configuration=configuration,
        patient_id=patch_appointment_response["patient_id"],
        start_time=start_time,
    )
    return create_appointment_response

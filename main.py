from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Annotated

# Local import
from classes.nexhealth_sdk import NexHealthSDK
from classes.request import NexHealthParams
from classes.request import RequestConfiguration
from ehr_abs_class import PER_PAGE

app = FastAPI()
bad_request_message = "Bad request; please check your call and then try again"
local_configuration_error_message = "Configuration type currently not supported"


@app.post("/appointments")
async def retrieve_appointments(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    end_date: str,
    start_date: str,
    patient_id: int | None = None,
    per_page: int = PER_PAGE,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    get_appointments_response = NexHealthSDK.get_appointments(
        configuration=params,
        end=end_date,
        patient_id=patient_id,
        per_page=per_page,
        start=start_date,
    )
    return get_appointments_response


@app.post("/cancel_appointment/{id}")
async def cancel_appointment(
    configuration: Annotated[RequestConfiguration, Body(embed=True)], id: int
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    patch_appointment_response = NexHealthSDK.patch_appointment(
        cancel=True, configuration=params, id=id
    )
    return patch_appointment_response


@app.post("/create_appointment")
async def create_appointment(
    configuration: RequestConfiguration,
    operatory_id: Annotated[int, Body()],
    patient_id: Annotated[int, Body()],
    start_time: Annotated[str, Body()],
    provider_id: Annotated[int | None, Body()] = None,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    # `c_` prefix stands for **calculated**
    c_provider_id = provider_id if provider_id else params.default_provider_id

    if c_provider_id is None:
        print("Error: No provider ID was provided")
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            bad_request_message,
        )

    appointment_result = NexHealthSDK.create_appointment(
        configuration=params,
        operatory_id=operatory_id,
        patient_id=patient_id,
        provider_id=c_provider_id,
        start_time=start_time,
    )
    return appointment_result


@app.post("/create_patient")
async def create_patient(
    configuration: RequestConfiguration,
    date_of_birth: Annotated[str, Body()],
    first_name: Annotated[str, Body()],
    last_name: Annotated[str, Body()],
    phone_number: Annotated[str, Body()],
    email: Annotated[str | None, Body()] = None,
    provider_id: Annotated[int | None, Body()] = None,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    c_email = email if email else params.default_patient_email
    c_provider_id = provider_id if provider_id else params.default_provider_id

    if c_email is None or c_provider_id is None:
        print(
            f"No email or provider ID was provided; email: {c_email}; provider ID: {c_provider_id}"
        )
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            bad_request_message,
        )

    create_patient_response = NexHealthSDK.create_patient(
        configuration=params,
        date_of_birth=date_of_birth,
        email=c_email,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        provider_id=c_provider_id,
    )
    return create_patient_response


@app.post("/patients")
async def get_patients(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    date_of_birth: str | None = None,
    legacy_format: bool = True,
    per_page: int = PER_PAGE,
    phone_number: str | None = None,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    patients = NexHealthSDK.get_patients(
        configuration=params,
        date_of_birth=date_of_birth,
        per_page=per_page,
        phone_number=phone_number,
        use_legacy_format=legacy_format,
    )
    return patients


@app.post("/reschedule_appointment/{id}")
async def reschedule_appointment(
    configuration: Annotated[RequestConfiguration, Body()],
    id: int,
    operatory_id: Annotated[int, Body()],
    start_time: Annotated[str, Body()],
    provider_id: Annotated[int | None, Body()] = None,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    c_provider_id = provider_id if provider_id else params.default_provider_id

    if c_provider_id is None:
        print("Error: No provider ID was provided")
        raise HTTPException(HTTP_400_BAD_REQUEST, bad_request_message)

    patch_appointment_response = NexHealthSDK.patch_appointment(
        cancel=True,
        configuration=params,
        id=id,
    )
    create_appointment_response = NexHealthSDK.create_appointment(
        configuration=params,
        operatory_id=operatory_id,
        patient_id=patch_appointment_response["patient_id"],
        provider_id=c_provider_id,
        start_time=start_time,
    )
    return create_appointment_response

@app.post("/procedures")
async def get_procedures(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    updated_after: str,
    provider_id: int | None = None,
    patient_id: int | None = None,
    appointment_id: int | None = None,
    per_page: int = PER_PAGE,
):
    params = configuration.params

    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    procedures = NexHealthSDK.get_procedures(
        configuration=params,
        updated_after=updated_after,
        provider_id=provider_id,
        patient_id=patient_id,
        appointment_id=appointment_id,
        per_page=per_page,
    )
    return procedures
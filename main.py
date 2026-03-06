from fastapi import Body
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Annotated
from typing import Literal
from typing import Sequence

# Local import
from classes.nexhealth import NexHealthIncludeAppointmentQueryValue
from classes.nexhealth import NexHealthIncludePatientQueryValue
from classes.nexhealth import NexHealthSubscriptionFeature
from classes.nexhealth_sdk import NexHealthSDK
from classes.request import NexHealthParams
from classes.request import RequestConfiguration
from ehr_abs_class import PER_PAGE
from lib.requests_utilities import validate_app_key

app = FastAPI()
bad_request_message = "Bad request; please check your call and then try again"
local_configuration_error_message = "Configuration type currently not supported"


@app.post("/appointments")
async def get_appointments(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    end_date: str,
    start_date: str,
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_type_id: int | None = None,
    cancelled: bool | None = None,
    created_by: str | None = None,
    foreign_id: str | None = None,
    include: Annotated[
        Sequence[NexHealthIncludeAppointmentQueryValue] | None,
        Query(),
    ] = None,
    nex_only: bool | None = None,
    operatory_ids: Annotated[Sequence[int] | None, Query()] = None,
    page: int | None = None,
    patient_id: int | None = None,
    per_page: int = PER_PAGE,
    provider_ids: Annotated[Sequence[int] | None, Query()] = None,
    raw_response: bool = False,
    timezone: str | None = None,
    unavailable: bool | None = None,
    updated_since: str | None = None,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    get_appointments_response = NexHealthSDK.get_appointments(
        appointment_type_id=appointment_type_id,
        cancelled=cancelled,
        configuration=params,
        created_by=created_by,
        end=end_date,
        foreign_id=foreign_id,
        include=include,
        nex_only=nex_only,
        operatory_ids=operatory_ids,
        page=page,
        patient_id=patient_id,
        per_page=per_page,
        provider_ids=provider_ids,
        raw_response=raw_response,
        start=start_date,
        timezone=timezone,
        unavailable=unavailable,
        updated_since=updated_since,
    )
    return get_appointments_response


@app.post("/cancel_appointment/{id}")
async def cancel_appointment(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    id: int,
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
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
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_type_id: Annotated[int | None, Body()] = None,
    descriptor_ids: Sequence[int] | None = None,
    end_time: Annotated[str | None, Body()] = None,
    note: Annotated[str | None, Body()] = None,
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
        appointment_type_id=appointment_type_id,
        configuration=params,
        descriptor_ids=descriptor_ids,
        end_time=end_time,
        note=note,
        operatory_id=operatory_id,
        patient_id=patient_id,
        provider_id=c_provider_id,
        start_time=start_time,
    )
    return appointment_result


@app.post("/create_availability")
async def create_availability(
    begin_time: Annotated[str, Body()],
    configuration: Annotated[RequestConfiguration, Body()],
    days: Sequence[
        Literal[
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
    ],
    end_time: Annotated[str, Body()],
    operatory_id: Annotated[int, Body()],
    provider_id: Annotated[int, Body()],
    appointment_type_ids: Sequence[int] | None = None,
    specific_date: Annotated[str | None, Body()] = None,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    create_availability_response = NexHealthSDK.create_availability(
        appointment_type_ids=appointment_type_ids,
        begin_time=begin_time,
        configuration=params,
        days=days,
        end_time=end_time,
        operatory_id=operatory_id,
        provider_id=provider_id,
        specific_date=specific_date,
    )
    return create_availability_response


@app.post("/create_patient")
async def create_patient(
    configuration: RequestConfiguration,
    date_of_birth: Annotated[str, Body()],
    first_name: Annotated[str, Body()],
    last_name: Annotated[str, Body()],
    phone_number: Annotated[str, Body()],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
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


@app.post("/locations")
async def get_locations(
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    configuration: Annotated[
        RequestConfiguration[NexHealthParams] | None, Body(embed=True)
    ] = None,
    filter_by_subscription_feature: NexHealthSubscriptionFeature | None = None,
    foreign_id: str | None = None,
    inactive: bool | None = None,
    subdomain: str | None = None,
):
    get_locations_response = NexHealthSDK.get_locations(
        configuration=configuration.params if configuration else None,
        filter_by_subscription_feature=filter_by_subscription_feature,
        foreign_id=foreign_id,
        inactive=inactive,
        subdomain=subdomain,
    )
    return get_locations_response


@app.post("/operatories")
async def get_operatories(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    get_operatories_response = NexHealthSDK.get_operatories(configuration=params)
    return get_operatories_response


@app.post("/patients")
async def get_patients(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_date_end: str | None = None,
    appointment_date_start: str | None = None,
    date_of_birth: str | None = None,
    email: str | None = None,
    foreign_id: str | None = None,
    inactive: bool = False,
    include: Annotated[
        Sequence[NexHealthIncludePatientQueryValue] | None,
        Query(),
    ] = None,
    name: str | None = None,
    non_patient: bool = False,
    location_strict: bool | None = None,
    page: int | None = None,
    per_page: int = PER_PAGE,
    phone_number: str | None = None,
    raw_response: bool = False,
    updated_since: str | None = None,
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    patients = NexHealthSDK.get_patients(
        appointment_date_end=appointment_date_end,
        appointment_date_start=appointment_date_start,
        configuration=params,
        date_of_birth=date_of_birth,
        email=email,
        foreign_id=foreign_id,
        inactive=inactive,
        include=include,
        location_strict=location_strict,
        name=name,
        non_patient=non_patient,
        page=page,
        per_page=per_page,
        phone_number=phone_number,
        raw_response=raw_response,
        updated_since=updated_since,
    )
    return patients


@app.post("/providers")
async def get_providers(
    configuration: Annotated[RequestConfiguration, Body(embed=True)],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
):
    params = configuration.params

    # TODO: Enable `Local` configuration
    if configuration.type == "Local" or not isinstance(params, NexHealthParams):
        raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

    get_providers_response = NexHealthSDK.get_providers(configuration=params)
    return get_providers_response


@app.post("/reschedule_appointment/{id}")
async def reschedule_appointment(
    configuration: Annotated[RequestConfiguration, Body()],
    id: int,
    operatory_id: Annotated[int, Body()],
    start_time: Annotated[str, Body()],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
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
        patient_id=patch_appointment_response.patient_id,
        provider_id=c_provider_id,
        start_time=start_time,
    )
    return create_appointment_response

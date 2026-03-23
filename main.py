import datetime as dt
from fastapi import Body
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Annotated
from typing import Literal
from typing import Sequence

# Local imports
from routers import recalls
from classes.nexhealth import NexHealthAvailability
from classes.nexhealth import NexHealthGuardianPatient
from classes.nexhealth import NexHealthProvider
from classes.nexhealth_sdk import NexHealthSDK
from classes.pms import Appointment
from classes.pms import Patient
from classes.request import GetAppointmentSlotsResponse
from classes.request import GetAppointmentsResponse
from classes.request import GetLocationsResponse
from classes.request import GetOperatoriesResponse
from classes.request import GetPatientsResponse
from classes.request import GetProceduresResponse
from classes.request import GetProvidersResponse
from classes.request import NexHealthParams
from classes.request import RequestConfiguration
from ehr_abs_class import PER_PAGE
from lib.utilities.requests_utilities import validate_app_key
from type_definitions.miscellaneous_types import DayType
from type_definitions.miscellaneous_types import GenderType
from type_definitions.nexhealth_types import NexHealthIncludeAppointmentQueryValueType
from type_definitions.nexhealth_types import NexHealthIncludePatientQueryValueType
from type_definitions.nexhealth_types import NexHealthProviderIncludeQueryType
from type_definitions.nexhealth_types import NexHealthSubscriptionFeatureType

app = FastAPI()
bad_request_message = "Bad request; please check your call and then try again"
local_configuration_error_message = "Configuration type currently not supported"

app.include_router(recalls.router)


@app.post("/appointment_slots")
async def get_appointment_slots(
    days: int,
    lids: Annotated[Sequence[int], Query()],
    pids: Annotated[Sequence[int], Query()],
    start_date: str,
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_type_id: int | None = None,
    configuration: Annotated[RequestConfiguration | None, Body(embed=True)] = None,
    operatory_ids: Annotated[Sequence[int] | None, Query()] = None,
    overlapping_operatory_slots: bool | None = None,
    slot_interval: int | None = None,
    slot_length: int | None = None,
    subdomain: str | None = None,
) -> GetAppointmentSlotsResponse:
    # TODO: Enable `Local` configuration
    if configuration:
        params = configuration.params

        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    get_appointment_slots_response = NexHealthSDK.get_appointment_slots(
        appointment_type_id=appointment_type_id,
        configuration=params,
        days=days,
        lids=lids,
        operatory_ids=operatory_ids,
        overlapping_operatory_slots=overlapping_operatory_slots,
        pids=pids,
        slot_interval=slot_interval,
        slot_length=slot_length,
        start_date=start_date,
        subdomain=subdomain,
    )
    return get_appointment_slots_response


@app.post("/appointments")
async def get_appointments(
    end_date: str,
    start_date: str,
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_type_id: int | None = None,
    cancelled: bool | None = None,
    configuration: Annotated[RequestConfiguration | None, Body(embed=True)] = None,
    created_by: str | None = None,
    foreign_id: str | None = None,
    include: Annotated[
        Sequence[NexHealthIncludeAppointmentQueryValueType] | None,
        Query(),
    ] = None,
    location_id: int | None = None,
    nex_only: bool | None = None,
    operatory_ids: Annotated[Sequence[int] | None, Query()] = None,
    page: int | None = None,
    patient_id: int | None = None,
    per_page: int = PER_PAGE,
    provider_ids: Annotated[Sequence[int] | None, Query()] = None,
    raw_response: bool = False,
    subdomain: str | None = None,
    timezone: str | None = None,
    unavailable: bool | None = None,
    updated_since: str | None = None,
) -> GetAppointmentsResponse:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    get_appointments_response = NexHealthSDK.get_appointments(
        appointment_type_id=appointment_type_id,
        cancelled=cancelled,
        configuration=params,
        created_by=created_by,
        end=end_date,
        foreign_id=foreign_id,
        include=include,
        location_id=location_id,
        nex_only=nex_only,
        operatory_ids=operatory_ids,
        page=page,
        patient_id=patient_id,
        per_page=per_page,
        provider_ids=provider_ids,
        raw_response=raw_response,
        start=start_date,
        subdomain=subdomain,
        timezone=timezone,
        unavailable=unavailable,
        updated_since=updated_since,
    )
    return get_appointments_response


@app.post("/cancel_appointment/{id}")
async def cancel_appointment(
    id: int,
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    configuration: Annotated[RequestConfiguration | None, Body(embed=True)] = None,
    subdomain: str | None = None,
) -> Appointment:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    patch_appointment_response = NexHealthSDK.patch_appointment(
        cancel=True,
        configuration=params,
        id=id,
        subdomain=subdomain,
    )
    return patch_appointment_response


@app.post("/create_appointment")
async def create_appointment(
    operatory_id: Annotated[int, Body()],
    start_time: Annotated[str, Body()],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_type_id: Annotated[int | None, Body()] = None,
    configuration: RequestConfiguration | None = None,
    descriptor_ids: Sequence[int] | None = None,
    end_time: Annotated[str | None, Body()] = None,
    is_guardian: Annotated[bool | None, Body()] = None,
    is_new_clients_patient: Annotated[bool | None, Body()] = None,
    location_id: int | None = None,
    note: Annotated[str | None, Body()] = None,
    notify_patient: bool | None = None,
    patient: NexHealthGuardianPatient | None = None,
    patient_id: Annotated[int | None, Body()] = None,
    provider_id: Annotated[int | None, Body()] = None,
    referrer: Annotated[str | None, Body()] = None,
    subdomain: str | None = None,
    unavailable: Annotated[bool | None, Body()] = None,
) -> Appointment:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

        # `c_` prefix stands for **calculated**
        c_provider_id = provider_id if provider_id else params.default_provider_id
    else:
        c_provider_id = provider_id
        params = None
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
        is_guardian=is_guardian,
        is_new_clients_patient=is_new_clients_patient,
        location_id=location_id,
        note=note,
        notify_patient=notify_patient,
        operatory_id=operatory_id,
        patient=patient,
        patient_id=patient_id,
        provider_id=c_provider_id,
        referrer=referrer,
        start_time=start_time,
        subdomain=subdomain,
        unavailable=unavailable,
    )
    return appointment_result


@app.post("/create_availability")
async def create_availability(
    begin_time: Annotated[str, Body()],
    days: Sequence[DayType],
    end_time: Annotated[str, Body()],
    operatory_id: Annotated[int, Body()],
    provider_id: Annotated[int, Body()],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_type_ids: Sequence[int] | None = None,
    configuration: Annotated[RequestConfiguration | None, Body()] = None,
    location_id: int | None = None,
    specific_date: Annotated[str | None, Body()] = None,
    subdomain: str | None = None,
) -> NexHealthAvailability:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    create_availability_response = NexHealthSDK.create_availability(
        appointment_type_ids=appointment_type_ids,
        begin_time=begin_time,
        configuration=params,
        days=days,
        end_time=end_time,
        location_id=location_id,
        operatory_id=operatory_id,
        provider_id=provider_id,
        specific_date=specific_date,
        subdomain=subdomain,
    )
    return create_availability_response


@app.post("/create_patient")
async def create_patient(
    date_of_birth: Annotated[
        dt.date, Body(examples=[dt.date.fromisoformat("1990-09-29")])
    ],
    first_name: Annotated[str, Body()],
    last_name: Annotated[str, Body()],
    phone_number: Annotated[str, Body()],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    address_line_1: Annotated[str | None, Body()] = None,
    address_line_2: Annotated[str | None, Body()] = None,
    cell_phone_number: Annotated[str | None, Body()] = None,
    city: Annotated[str | None, Body()] = None,
    configuration: RequestConfiguration | None = None,
    country_code: str | None = None,
    custom_contact_number: Annotated[str | None, Body()] = None,
    email: Annotated[str | None, Body()] = None,
    gender: Annotated[GenderType | None, Body()] = None,
    height: Annotated[int | None, Body()] = None,
    home_phone_number: Annotated[str | None, Body()] = None,
    insurance_name: Annotated[str | None, Body()] = None,
    location_id: int | None = None,
    provider_id: Annotated[int | None, Body()] = None,
    race: Annotated[str | None, Body()] = None,
    ssn: Annotated[str | None, Body()] = None,
    state: Annotated[str | None, Body()] = None,
    street_address: Annotated[str | None, Body()] = None,
    subdomain: str | None = None,
    weight: Annotated[int | None, Body()] = None,
    work_phone_number: Annotated[str | None, Body()] = None,
    zip_code: Annotated[str | None, Body()] = None,
) -> Patient:
    # TODO: Enable `Local` configuration
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

        c_country_code: str | None = (
            country_code if country_code else configuration.country_code
        )
        c_email = email if email else params.default_patient_email
        c_provider_id = provider_id if provider_id else params.default_provider_id
    else:
        c_country_code = country_code
        c_email = email
        c_provider_id = provider_id
        params = None

    if c_email is None or c_provider_id is None:
        print(
            f"No email or provider ID was provided; email: {c_email}; provider ID: {c_provider_id}"
        )
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            bad_request_message,
        )

    create_patient_response = NexHealthSDK.create_patient(
        address_line_1=address_line_1,
        address_line_2=address_line_2,
        cell_phone_number=cell_phone_number,
        city=city,
        configuration=params,
        country_code=c_country_code,
        custom_contact_number=custom_contact_number,
        date_of_birth=date_of_birth,
        email=c_email,
        first_name=first_name,
        gender=gender,
        height=height,
        home_phone_number=home_phone_number,
        insurance_name=insurance_name,
        last_name=last_name,
        location_id=location_id,
        phone_number=phone_number,
        provider_id=c_provider_id,
        race=race,
        ssn=ssn,
        state=state,
        street_address=street_address,
        subdomain=subdomain,
        weight=weight,
        work_phone_number=work_phone_number,
        zip_code=zip_code,
    )
    return create_patient_response


@app.post("/locations")
async def get_locations(
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    configuration: Annotated[
        RequestConfiguration[NexHealthParams] | None, Body(embed=True)
    ] = None,
    filter_by_subscription_feature: NexHealthSubscriptionFeatureType | None = None,
    foreign_id: str | None = None,
    inactive: bool | None = None,
    subdomain: str | None = None,
) -> GetLocationsResponse:
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
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    configuration: Annotated[RequestConfiguration | None, Body(embed=True)] = None,
    location_id: int | None = None,
    search_name: str | None = None,
    subdomain: str | None = None,
) -> GetOperatoriesResponse:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    get_operatories_response = NexHealthSDK.get_operatories(
        configuration=params,
        location_id=location_id,
        search_name=search_name,
        subdomain=subdomain,
    )
    return get_operatories_response


@app.post("/patients")
async def get_patients(
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_date_end: dt.date | dt.datetime | None = None,
    appointment_date_start: dt.date | dt.datetime | None = None,
    configuration: Annotated[RequestConfiguration | None, Body(embed=True)] = None,
    date_of_birth: dt.date | None = None,
    email: str | None = None,
    foreign_id: str | None = None,
    inactive: bool = False,
    include: Annotated[
        Sequence[NexHealthIncludePatientQueryValueType] | None,
        Query(),
    ] = None,
    location_id: int | None = None,
    name: str | None = None,
    new_patient: bool | None = None,
    non_patient: bool = False,
    location_strict: bool | None = None,
    page: int | None = None,
    per_page: int = PER_PAGE,
    phone_number: str | None = None,
    raw_response: bool = False,
    subdomain: str | None = None,
    updated_since: str | None = None,
) -> GetPatientsResponse:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    get_patients_response = NexHealthSDK.get_patients(
        appointment_date_end=appointment_date_end,
        appointment_date_start=appointment_date_start,
        configuration=params,
        date_of_birth=date_of_birth,
        email=email,
        foreign_id=foreign_id,
        inactive=inactive,
        include=include,
        location_id=location_id,
        location_strict=location_strict,
        name=name,
        new_patient=new_patient,
        non_patient=non_patient,
        page=page,
        per_page=per_page,
        phone_number=phone_number,
        raw_response=raw_response,
        subdomain=subdomain,
        updated_since=updated_since,
    )
    return get_patients_response


@app.post("/procedures")
async def get_procedures(
    updated_after: str,
    appointment_id: int | None = None,
    configuration: Annotated[RequestConfiguration | None, Body(embed=True)] = None,
    location_id: int | None = None,
    patient_id: int | None = None,
    per_page: int = PER_PAGE,
    provider_id: int | None = None,
    subdomain: str | None = None,
) -> GetProceduresResponse:
    # TODO: Enable `Local` configuration
    if configuration:
        params = configuration.params

        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    procedures = NexHealthSDK.get_procedures(
        appointment_id=appointment_id,
        configuration=params,
        location_id=location_id,
        patient_id=patient_id,
        per_page=per_page,
        provider_id=provider_id,
        subdomain=subdomain,
        updated_after=updated_after,
    )
    return procedures


@app.get("/provider/{id}")
async def get_provider(
    id: int,
    subdomain: str,
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    include: Annotated[
        Sequence[NexHealthProviderIncludeQueryType] | None,
        Query(),
    ] = None,
) -> NexHealthProvider:
    get_provider_response = NexHealthSDK.get_provider(
        id=id, include=include, subdomain=subdomain
    )
    return get_provider_response


@app.post("/providers")
async def get_providers(
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    configuration: Annotated[RequestConfiguration | None, Body(embed=True)] = None,
    location_id: int | None = None,
    subdomain: str | None = None,
) -> GetProvidersResponse:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)
    else:
        params = None

    get_providers_response = NexHealthSDK.get_providers(
        configuration=params, location_id=location_id, subdomain=subdomain
    )
    return get_providers_response


@app.post("/reschedule_appointment/{id}")
async def reschedule_appointment(
    id: int,
    operatory_id: Annotated[int, Body()],
    start_time: Annotated[str, Body()],
    x_app_id: Annotated[Literal[True], Depends(validate_app_key)],
    appointment_type_id: Annotated[int | None, Body()] = None,
    configuration: Annotated[RequestConfiguration | None, Body()] = None,
    descriptor_ids: Sequence[int] | None = None,
    end_time: Annotated[str | None, Body()] = None,
    is_guardian: Annotated[bool | None, Body()] = None,
    is_new_clients_patient: Annotated[bool | None, Body()] = None,
    location_id: int | None = None,
    note: Annotated[str | None, Body()] = None,
    notify_patient: bool | None = None,
    patient: NexHealthGuardianPatient | None = None,
    provider_id: Annotated[int | None, Body()] = None,
    referrer: Annotated[str | None, Body()] = None,
    subdomain: str | None = None,
    unavailable: Annotated[bool | None, Body()] = None,
) -> Appointment:
    if configuration:
        params = configuration.params

        # TODO: Enable `Local` configuration
        if configuration.type == "Local" or not isinstance(params, NexHealthParams):
            raise HTTPException(HTTP_400_BAD_REQUEST, local_configuration_error_message)

        c_provider_id = provider_id if provider_id else params.default_provider_id
    else:
        c_provider_id = provider_id
        params = None
    if c_provider_id is None:
        print("Error: No provider ID was provided")
        raise HTTPException(HTTP_400_BAD_REQUEST, bad_request_message)

    patch_appointment_response = NexHealthSDK.patch_appointment(
        cancel=True,
        configuration=params,
        id=id,
    )
    create_appointment_response = NexHealthSDK.create_appointment(
        appointment_type_id=appointment_type_id,
        configuration=params,
        descriptor_ids=descriptor_ids,
        end_time=end_time,
        is_guardian=is_guardian,
        is_new_clients_patient=is_new_clients_patient,
        location_id=location_id,
        note=note,
        notify_patient=notify_patient,
        operatory_id=operatory_id,
        patient=patient,
        patient_id=patch_appointment_response.patient_id,
        provider_id=c_provider_id,
        referrer=referrer,
        start_time=start_time,
        subdomain=subdomain,
        unavailable=unavailable,
    )
    return create_appointment_response

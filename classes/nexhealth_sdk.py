import datetime as dt
import httpx
import requests
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Dict
from typing import Literal
from typing import Mapping
from typing import Sequence

# local modules
from classes.nexhealth import BaseNexHealthPatient
from classes.nexhealth import NexHealthAppointment
from classes.nexhealth import NexHealthAvailability
from classes.nexhealth import NexHealthGuardianPatient
from classes.nexhealth import NexHealthPatient
from classes.pms import Appointment
from classes.request import GetAppointmentSlotsResponse
from classes.request import GetAppointmentsResponse
from classes.request import GetLocationsResponse
from classes.request import GetOperatoriesResponse
from classes.request import GetPatientsResponse
from classes.request import GetProceduresResponse
from classes.request import GetProvidersResponse
from ehr_abs_class import NexHealthConfig
from ehr_abs_class import PER_PAGE
from ehr_abs_class import PMSAbstractBaseClass
from lib.utilities.miscellaneous_utilities import generate_pms_appointment
from lib.utilities.miscellaneous_utilities import generate_pms_appointments
from lib.utilities.miscellaneous_utilities import generate_pms_patient
from lib.utilities.miscellaneous_utilities import generate_pms_patients
from lib.utilities.nexhealth_utilities import process_phone_number
from settings import settings
from type_definitions.miscellaneous_types import DayType
from type_definitions.miscellaneous_types import GenderType
from type_definitions.nexhealth_types import NexHealthIncludeAppointmentQueryType
from type_definitions.nexhealth_types import NexHealthIncludePatientQueryType
from type_definitions.nexhealth_types import NexHealthParentType
from type_definitions.nexhealth_types import NexHealthSubscriptionFeatureType


def stringify_bool(arg: bool) -> Literal["false", "true"]:
    return "true" if arg else "false"


def compute_subdomain_and_location_id(
    *,
    configuration: NexHealthConfig | None,
    location_id: int | None = None,
    subdomain: str | None,
):
    if configuration is None:
        c_location_id = location_id
        c_subdomain = subdomain
    else:
        c_location_id = location_id if location_id else configuration.location_id
        c_subdomain = subdomain if subdomain else configuration.subdomain
    return c_location_id, c_subdomain


class NexHealthSDK(PMSAbstractBaseClass[NexHealthConfig | None]):
    @staticmethod
    def __get_access_token() -> str:
        headers = {
            "Authorization": settings.nexhealth_api_key,
            "Accept": "application/vnd.Nexhealth+json;version=2",
        }
        access_token_response = requests.post(
            f"{settings.nexhealth_url}/authenticates",
            headers=headers,
        )

        if access_token_response.status_code == 401:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Authorization error.",
            )
        return access_token_response.json()["data"]["token"]

    @classmethod
    def generate_headers(
        cls,
        *,
        beta_api: bool = False,
        post_call: bool = False,
    ) -> Mapping[str, str]:
        access_token = cls.__get_access_token()
        headers: Dict = {
            "Accept": "application/vnd.Nexhealth+json;version=2",
            "Authorization": f"Bearer {access_token}",
        }

        if beta_api:
            headers.update({"Nex-Api-Version": "v20240412"})
        if post_call:
            headers.update({"Content-Type": "application/json"})
        return headers

    @staticmethod
    def __generate_url(*, location_id: int | None = None, path: str, subdomain: str):
        url = f"{settings.nexhealth_url}{path}?subdomain={subdomain}"

        if location_id:
            url = f"{url}&location_id={location_id}"
        return url

    @classmethod
    def create_appointment(
        cls,
        *,
        appointment_type_id: int | None = None,
        configuration: NexHealthConfig | None = None,
        descriptor_ids: Sequence[int] | None = None,
        end_time: str | None = None,
        is_guardian: bool | None = None,
        is_new_clients_patient: bool | None = None,
        location_id: int | None = None,
        note: str | None = None,
        notify_patient: bool | None = None,  # Defaults to false in `NexHealth`
        operatory_id: int,
        patient: NexHealthGuardianPatient | None = None,
        patient_id: int | None = None,
        provider_id: int,
        referrer: str | None = None,
        start_time: str,  # HH:mm
        subdomain: str | None = None,
        unavailable: bool | None = None,
    ):
        # TODO: Confirm the appointment is available, on a patient basis
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating appointment")

        appt: Dict = {
            "operatory_id": operatory_id,
            "provider_id": provider_id,
            "start_time": start_time,
        }

        # # `is_guardian` validation
        if is_guardian is not None:
            if not is_guardian:
                appt.update({"is_guardian": is_guardian})
            # if `is_guardian` is set, `patient` most be provided
            elif patient is None:
                print("Error: `is_guardian` was set but `patient` is missing")
                raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating appointment")
            else:
                appt.update(
                    {
                        "is_guardian": is_guardian,
                        "patient": patient,
                    }
                )
        # # `patient_id` handling
        # when an appointment is set as `unavailable`, the `patient_id` is not
        # required
        if unavailable:
            appt.update({"unavailable": unavailable})
        # otherwise, it has to be provided
        elif patient_id is None:
            print("Error: `patient_id` is missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating appointment")
        else:
            appt.update({"patient_id": patient_id})

            # This validation seems unnecessary, but it is kept for completeness
            if unavailable is not None:
                appt.update({"unavailable": unavailable})
        if is_new_clients_patient is not None:
            appt.update({"is_new_clients_patient": is_new_clients_patient})
        if referrer:
            appt.update({"referrer": referrer})

        headers = cls.generate_headers(post_call=True)
        data = {
            "appt": appt,
        }
        generated_url = cls.__generate_url(
            location_id=c_location_id,
            path="/appointments",
            subdomain=c_subdomain,
        )
        url = generated_url

        if appointment_type_id:
            appt.update({"appointment_type_id": appointment_type_id})
        if descriptor_ids:
            appt.update({"descriptor_ids": descriptor_ids})
        if end_time:
            appt.update({"end_time": end_time})
        if note:
            appt.update({"note": note})
        if notify_patient is not None:
            url = f"{url}&notify_patient={stringify_bool(notify_patient)}"

        create_appointment_response = requests.post(url, headers=headers, json=data)
        create_appointment_response_data = create_appointment_response.json()
        create_appointment_response_status_code = (
            create_appointment_response.status_code
        )

        # status_code = create_appointment_response.status_code
        if create_appointment_response_status_code != 201:
            print("Error creating appointment")
            print(f"Response status code: {create_appointment_response_status_code}")

            if create_appointment_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {create_appointment_response_data}")
                print(f"Error: {create_appointment_response_data['error'][0]}")
            else:
                print(f"Error: {create_appointment_response_data}")
            raise HTTPException(
                detail="Error creating appointment",
                status_code=HTTP_400_BAD_REQUEST,
            )

        print(f"create appointment response data: {create_appointment_response_data}")

        appointment_data: NexHealthAppointment = create_appointment_response_data[
            "data"
        ]["appt"]
        appointment = generate_pms_appointment(appointment_data)
        return appointment

    @classmethod
    def create_appointment_type(
        cls,
        *,
        bookable_online=True,
        emr_appt_descriptor_ids: Sequence[int] = [],
        location_id: int | None = None,
        minutes=30,
        name: str,
        # Defaults to "Institution" in Nexhealth
        parent_type: NexHealthParentType | None = None,
        subdomain: str,
    ):
        headers = cls.generate_headers(post_call=True)
        generated_url = cls.__generate_url(
            path="/appointment_types", subdomain=subdomain
        )
        appointment_type = {
            "bookable_online": bookable_online,
            "emr_appt_descriptor_ids": emr_appt_descriptor_ids,
            "minutes": minutes,
            "name": name,
        }
        data: Dict = {"appointment_type": appointment_type}

        if parent_type == "Location":
            appointment_type.update(
                {
                    "parent_id": location_id,
                    "parent_type": parent_type,
                }
            )
            data.update(
                {
                    "location_id": location_id,
                }
            )

        create_appointment_type_response = requests.post(
            generated_url, headers=headers, json=data
        )
        create_appointment_type_response_data = create_appointment_type_response.json()
        create_appointment_type_response_status_code = (
            create_appointment_type_response.status_code
        )

        if create_appointment_type_response_status_code != 201:
            print("Error creating appointment type")
            print(
                f"Response status code: {create_appointment_type_response_status_code}"
            )

            if create_appointment_type_response_status_code in [
                400,
                401,
                403,
                404,
                500,
            ]:
                print(f"Response data: {create_appointment_type_response_data}")
                print(f"Error: {create_appointment_type_response_data['error'][0]}")
            else:
                print(f"Error: {create_appointment_type_response_data}")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating appointment type")
        print(f"Create appointment type data: {create_appointment_type_response_data}")
        return create_appointment_type_response_data["data"]

    @classmethod
    def create_availability(
        cls,
        *,
        active: bool | None = None,  # Defaults to `True` in Nexhealth
        appointment_type_ids: Sequence[int] | None = None,
        begin_time: str,
        configuration: NexHealthConfig | None = None,
        days: Sequence[DayType],
        end_time: str,
        location_id: int | None = None,
        operatory_id: int,
        provider_id: int,
        specific_date: str | None = None,
        subdomain: str | None = None,
    ) -> NexHealthAvailability:
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating availability")

        headers = cls.generate_headers(post_call=True)
        generated_url = cls.__generate_url(
            location_id=c_location_id,
            path="/availabilities",
            subdomain=c_subdomain,
        )
        availability = {
            "begin_time": begin_time,
            "days": days,
            "end_time": end_time,
            "operatory_id": operatory_id,
            "provider_id": provider_id,
        }
        data = {"availability": availability}

        if active is not None:
            availability.update({"active": active})
        if appointment_type_ids:
            availability.update({"appointment_type_ids": appointment_type_ids})
        if specific_date:
            availability.update({"specific_date": specific_date})

        create_availability_response = requests.post(
            generated_url, headers=headers, json=data
        )
        create_availability_response_data = create_availability_response.json()
        create_availability_response_status_code = (
            create_availability_response.status_code
        )

        if create_availability_response_status_code != 201:
            print("Error creating availability")
            print(f"Response status code: {create_availability_response_status_code}")

            if create_availability_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {create_availability_response_data}")
                print(f"Error: {create_availability_response_data['error'][0]}")
            else:
                print(f"Error: {create_availability_response_data}")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating availability")
        print(f"Create availability response data: {create_availability_response_data}")
        return create_availability_response_data["data"]

    @classmethod
    def create_patient(
        cls,
        *,
        address_line_1: str | None = None,
        address_line_2: str | None = None,
        cell_phone_number: str | None = None,
        city: str | None = None,
        configuration: NexHealthConfig | None = None,
        country_code: str | None = None,
        custom_contact_number: str | None = None,
        date_of_birth: dt.date,
        email: str,
        first_name: str,
        gender: GenderType | None = None,
        height: int | None = None,
        home_phone_number: str | None = None,
        insurance_name: str | None = None,
        last_name: str,
        location_id: int | None = None,
        phone_number: str,
        provider_id: int,
        race: str | None = None,
        ssn: str | None = None,
        state: str | None = None,
        street_address: str | None = None,
        subdomain: str | None = None,
        weight: int | None = None,
        work_phone_number: str | None = None,
        zip_code: str | None = None,
    ):
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating patient")

        processed_phone_number = process_phone_number(phone_number, country_code)
        bio: Dict = {
            "date_of_birth": date_of_birth,
            "phone_number": processed_phone_number,
        }

        if address_line_1:
            bio.update({"address_line_1": address_line_1})
        if address_line_2:
            bio.update({"address_line_2": address_line_2})
        if cell_phone_number:
            processed_cell_phone_number = process_phone_number(
                cell_phone_number, country_code
            )
            bio.update({"cell_phone_number": processed_cell_phone_number})
        if city:
            bio.update({"city": city})
        if custom_contact_number:
            processed_custom_contact_number = process_phone_number(
                custom_contact_number, country_code
            )
            bio.update({"custom_contact_number": processed_custom_contact_number})
        if gender:
            bio.update({"gender": gender})
        if height:
            bio.update({"height": height})
        if home_phone_number:
            processed_home_phone_number = process_phone_number(
                home_phone_number, country_code
            )
            bio.update({"home_phone_number": processed_home_phone_number})
        if insurance_name:
            bio.update({"insurance_name": insurance_name})
        if race:
            bio.update({"race": race})
        if ssn:
            bio.update({"ssn": ssn})
        if state:
            bio.update({"state": state})
        if street_address:
            bio.update({"street_address": street_address})
        if weight:
            bio.update({"weight": weight})
        if work_phone_number:
            processed_work_phone_number = process_phone_number(
                work_phone_number, country_code
            )
            bio.update({"work_phone_number": processed_work_phone_number})
        if zip_code:
            bio.update({"zip_code": zip_code})

        # Validate first that the patient does not already exist
        get_patients_response = cls.get_patients(
            configuration=configuration,
            date_of_birth=date_of_birth,
            location_id=location_id,
            phone_number=processed_phone_number,
            subdomain=subdomain,
        )

        if get_patients_response.count:
            print("Error creating patient, client already exists")
            print(f"Patients data: {get_patients_response}")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating patient")

        headers = cls.generate_headers(post_call=True)
        data = {
            "patient": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "bio": bio,
            },
            "provider": {
                "provider_id": provider_id,
            },
        }
        generated_url = cls.__generate_url(
            location_id=c_location_id,
            path="/patients",
            subdomain=c_subdomain,
        )
        create_patient_response = requests.post(
            generated_url, json=data, headers=headers
        )
        create_patient_response_data = create_patient_response.json()
        create_patient_response_status_code = create_patient_response.status_code

        if create_patient_response_status_code != 201:
            print("Error creating patient")
            print(f"Response status code: {create_patient_response_status_code}")

            if create_patient_response_status_code in [
                400,
                401,
                403,
                404,
                500,
            ]:
                print(f"Response data: {create_patient_response_data}")
                print(f"Error: {create_patient_response_data['error'][0]}")
            else:
                print(f"Error: {create_patient_response_data}")
            raise HTTPException(
                detail="Error creating patient",
                status_code=HTTP_400_BAD_REQUEST,
            )

        print(f"create patient response data: {create_patient_response_data}")

        user_data: BaseNexHealthPatient = create_patient_response_data["data"]["user"]
        patient = generate_pms_patient({"provider_id": provider_id, **user_data})
        return patient

    @classmethod
    def get_appointment(
        cls,
        *,
        id: int,
        include: Sequence[Literal["patient"]] | None = None,
        subdomain: str,
    ):
        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            path=f"/appointments/{id}", subdomain=subdomain
        )
        url = generated_url

        if include:
            for value in include:
                url = f"{url}&include[]={value}"

        get_appointment_response = requests.get(generated_url, headers=headers)
        get_appointment_response_data = get_appointment_response.json()
        get_appointment_response_status_code = get_appointment_response.status_code

        if get_appointment_response_status_code != 200:
            print("Error retrieving appointment")
            print(f"Response status code: {get_appointment_response_status_code}")

            if get_appointment_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {get_appointment_response_data}")
                print(f"Error: {get_appointment_response_data['error'][0]}")
            else:
                print(f"Error: {get_appointment_response_data}")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error retrieving appointment")
        print(f"get appointment response data: {get_appointment_response_data}")
        return get_appointment_response_data["data"]

    @classmethod
    def get_appointment_slots(
        cls,
        *,
        appointment_type_id: int | None = None,
        configuration: NexHealthConfig | None = None,
        days: int,
        lids: Sequence[int],
        operatory_ids: Sequence[int] | None = None,
        # defaults to `False` in `NexHealth`
        overlapping_operatory_slots: bool | None = None,
        pids: Sequence[int],
        slot_interval: int | None = None,
        slot_length: int | None = None,  # defaults to 15 minutes in `NexHealth`
        start_date: str,
        subdomain: str | None = None,
    ):
        _, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, subdomain=subdomain
        )

        if c_subdomain is None:
            print("Error: `subdomain` missing.")
            raise HTTPException(
                HTTP_400_BAD_REQUEST, "Error retrieving appointment slots"
            )

        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            path="/appointment_slots", subdomain=c_subdomain
        )
        url = f"{generated_url}&days={days}&start_date={start_date}"

        for lid in lids:
            url = f"{url}&lids[]={lid}"
        for pid in pids:
            url = f"{url}&pids[]={pid}"

        if appointment_type_id:
            url = f"{url}&appointment_type_id={appointment_type_id}"
        if operatory_ids:
            for operatory_id in operatory_ids:
                url = f"{url}&operatory_ids[]={operatory_id}"
        if overlapping_operatory_slots is not None:
            url = f"{url}&overlapping_operatory_slots={stringify_bool(overlapping_operatory_slots)}"
        if slot_interval:
            url = f"{url}&slot_interval={slot_interval}"
        if slot_length:
            url = f"{url}&slot_length={slot_length}"

        get_appointment_slots_response = requests.get(url, headers=headers)
        get_appointment_slots_response_data = get_appointment_slots_response.json()
        get_appointment_slots_response_status_code = (
            get_appointment_slots_response.status_code
        )

        if get_appointment_slots_response_status_code != 200:
            print("Error retrieving appointment slots")
            print(f"Response status code: {get_appointment_slots_response_status_code}")

            if get_appointment_slots_response_status_code in [400, 401, 403, 500]:
                print(f"Response data: {get_appointment_slots_response_data}")
                print(f"Error: {get_appointment_slots_response_data['error'][0]}")
            else:
                print(f"Error: {get_appointment_slots_response_data}")

        print(f"get appointment slots data: {get_appointment_slots_response_data}")

        get_appointment_slots_response_instance = GetAppointmentSlotsResponse(
            count=get_appointment_slots_response_data["count"],
            data=get_appointment_slots_response_data["data"],
        )
        return get_appointment_slots_response_instance

    @classmethod
    def get_appointments(
        cls,
        *,
        appointment_type_id: int | None = None,
        cancelled: bool | None = None,
        configuration: NexHealthConfig | None = None,
        created_by: str | None = None,
        end: str,
        foreign_id: str | None = None,
        include: NexHealthIncludeAppointmentQueryType | None = None,
        location_id: int | None = None,
        nex_only: bool | None = None,
        operatory_ids: Sequence[int] | None = None,
        page: int | None = None,
        patient_id: int | None = None,
        per_page: int = PER_PAGE,
        provider_ids: Sequence[int] | None = None,
        raw_response: bool = False,
        start: str,
        subdomain: str | None = None,
        timezone: str | None = None,
        unavailable: bool | None = None,
        updated_since: str | None = None,
    ):
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error retrieving appointments")

        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=c_location_id,
            path="/appointments",
            subdomain=c_subdomain,
        )
        url = f"{generated_url}&end={end}&start={start}&per_page={per_page}"

        if appointment_type_id:
            url = f"{url}&appointment_type_id={appointment_type_id}"
        if cancelled is not None:
            url = f"{url}&cancelled={cancelled}"
        if created_by:
            url = f"{url}&created_by={created_by}"
        if foreign_id:
            url = f"{url}&foreign_id={foreign_id}"
        if include:
            for value in include:
                url = f"{url}&include[]={value}"
        if nex_only is not None:
            url = f"{url}&nex_only={nex_only}"
        if operatory_ids:
            for operatory_id in operatory_ids:
                url = f"{url}&operatory_ids[]={operatory_id}"
        if page:
            url = f"{url}&page={page}"
        if patient_id:
            url = f"{url}&patient_id={patient_id}"
        if provider_ids:
            for provider_id in provider_ids:
                url = f"{url}&provider_ids[]={provider_id}"
        if timezone:
            url = f"{url}&timezone={timezone}"
        if unavailable is not None:
            url = f"{url}&unavailable={unavailable}"
        if updated_since:
            url = f"{url}&updated_since={updated_since}"

        get_appointments_response = requests.get(url, headers=headers)
        get_appointments_response_data = get_appointments_response.json()
        get_appointments_response_status_code = get_appointments_response.status_code

        if get_appointments_response_status_code != 200:
            print("Error retrieving appointments")
            print(f"Response status code: {get_appointments_response_status_code}")

            if get_appointments_response_status_code in [
                400,
                401,
                403,
                404,
                500,
            ]:
                print(f"Response data: {get_appointments_response_data}")
                print(f"Error: {get_appointments_response_data['error'][0]}")
            else:
                print(f"Error: {get_appointments_response_data}")
            raise HTTPException(
                detail="Error retrieving appointments",
                status_code=HTTP_400_BAD_REQUEST,
            )

        print(f"get appointments response data: {get_appointments_response_data}")

        appointments_data: Sequence[NexHealthAppointment] = (
            get_appointments_response_data["data"]
        )

        if raw_response:
            appointments = appointments_data
        else:
            appointments = generate_pms_appointments(appointments_data)
        return GetAppointmentsResponse(
            count=get_appointments_response_data["count"],
            data=appointments,
        )

    @classmethod
    def get_appointment_descriptors(
        cls,
        *,
        appointment_id: int,
        descriptor_type: str | None = None,
        subdomain: str,
    ):
        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            path=f"/appointments/{appointment_id}/appointment_descriptors",
            subdomain=subdomain,
        )
        url = (
            f"{generated_url}?descriptor_type={descriptor_type}"
            if descriptor_type
            else generated_url
        )
        get_appointment_descriptors_response = requests.get(url, headers=headers)
        get_appointment_descriptors_response_data = (
            get_appointment_descriptors_response.json()
        )
        get_appointment_descriptors_response_status_code = (
            get_appointment_descriptors_response.status_code
        )

        if get_appointment_descriptors_response_status_code != 200:
            print("Error retrieving appointment descriptors")
            print(
                f"Response status code: {get_appointment_descriptors_response_status_code}"
            )

            if get_appointment_descriptors_response_status_code in [
                400,
                401,
                403,
                404,
                500,
            ]:
                print(f"Response data: {get_appointment_descriptors_response_data}")
                print(f"Error: {get_appointment_descriptors_response_data["error"][0]}")
            else:
                print(f"Error: {get_appointment_descriptors_response_data}")
            raise HTTPException(
                HTTP_400_BAD_REQUEST,
                "Error retrieving appointment descriptors",
            )
        print(
            f"appointment descriptors response data: {get_appointment_descriptors_response_data}"
        )
        return get_appointment_descriptors_response_data["data"]

    @classmethod
    def get_appointment_types(
        cls,
        *,
        include: Sequence[Literal["descriptors"]] | None = None,
        location_id: int,
        subdomain: str,
    ):
        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=location_id,
            path="/appointment_types",
            subdomain=subdomain,
        )
        url = generated_url

        if include:
            for value in include:
                url = f"{url}&include[]={value}"

        get_appointment_types_response = requests.get(url, headers=headers)
        get_appointment_types_response_data = get_appointment_types_response.json()
        get_appointment_types_response_status_code = (
            get_appointment_types_response.status_code
        )

        if get_appointment_types_response_status_code != 200:
            print("Error retrieving appoint types")
            print(f"Response status code: {get_appointment_types_response_status_code}")

            if get_appointment_types_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {get_appointment_types_response_data}")
                print(f"Error: {get_appointment_types_response_data['error'][0]}")
            else:
                print(f"Error: {get_appointment_types_response_data}")
            raise HTTPException(
                HTTP_400_BAD_REQUEST, "Error retrieving appointment types"
            )
        print(f"Get appointment types data: {get_appointment_types_response_data}")
        return get_appointment_types_response_data["data"]

    @classmethod
    def get_location_appointment_descriptors(
        cls, location_id: int, descriptor_type: str | None = None
    ):
        url = (
            f"{settings.nexhealth_url}/locations/{location_id}/appointment_descriptors"
        )

        if descriptor_type:
            url = f"{url}?descriptor_type={descriptor_type}"

        headers = cls.generate_headers()
        location_appointment_descriptors_response = requests.get(url, headers=headers)
        location_appointment_descriptors_response_data = (
            location_appointment_descriptors_response.json()
        )
        location_appointment_descriptors_response_status_code = (
            location_appointment_descriptors_response.status_code
        )

        if location_appointment_descriptors_response_status_code != 200:
            print(
                f"Error retrieving location appointment descriptors: {location_appointment_descriptors_response_data}"
            )
            raise HTTPException(
                location_appointment_descriptors_response_status_code,
                "Error retrieving location appointment descriptors",
            )

        print(
            f"location appointment descriptors response data: {location_appointment_descriptors_response_data}"
        )
        return location_appointment_descriptors_response_data["data"]

    @classmethod
    def get_locations(
        cls,
        *,
        configuration: NexHealthConfig | None = None,
        filter_by_subscription_feature: NexHealthSubscriptionFeatureType | None = None,
        foreign_id: str | None = None,
        inactive: bool | None = None,
        subdomain: str | None = None,
    ):
        c_subdomain = (
            subdomain
            if subdomain
            else configuration.subdomain if configuration else None
        )
        headers = cls.generate_headers()
        querystring_initiated = False
        url = f"{settings.nexhealth_url}/locations"

        if filter_by_subscription_feature:
            url = f"{url}?filter_by_subscription_feature"
            querystring_initiated = True
        if foreign_id:
            url = f"{url}{'&' if querystring_initiated else '?'}foreign_id={foreign_id}"
            querystring_initiated = True
        if inactive is not None:
            url = f"{url}{'&' if querystring_initiated else '?'}inactive={stringify_bool(inactive)}"
            querystring_initiated = True
        if c_subdomain:
            url = f"{url}{'&' if querystring_initiated else '?'}subdomain={c_subdomain}"

        get_locations_response = requests.get(url, headers=headers)
        get_locations_response_data = get_locations_response.json()
        get_locations_response_status_code = get_locations_response.status_code

        if get_locations_response_status_code != 200:
            print("Error retrieving locations")
            print(f"Response status code: {get_locations_response_status_code}")

            if get_locations_response_status_code in [400, 401, 403, 500]:
                print(f"Response data: {get_locations_response_data}")
                print(f"Error: {get_locations_response_data['error'][0]}")
            else:
                print(f"Error: {get_locations_response_data}")

        print(f"get locations response data: {get_locations_response_data}")

        get_locations_response_instance = GetLocationsResponse(
            count=get_locations_response_data["count"],
            data=get_locations_response_data["data"],
        )
        return get_locations_response_instance

    @classmethod
    def get_operatories(
        cls,
        *,
        configuration: NexHealthConfig | None = None,
        location_id: int | None = None,
        search_name: str | None = None,
        subdomain: str | None = None,
    ):
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error retrieving operatories")

        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=c_location_id,
            path="/operatories",
            subdomain=c_subdomain,
        )
        url = generated_url

        if search_name:
            url = f"{url}&search_name={search_name}"

        get_operatories_response = requests.get(url, headers=headers)
        get_operatories_response_data = get_operatories_response.json()
        get_operatories_response_status_code = get_operatories_response.status_code

        if get_operatories_response_status_code != 200:
            print("Error retrieving operatories")
            print(f"Response status code: {get_operatories_response_status_code}")

            if get_operatories_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {get_operatories_response_data}")
                print(f"Error: {get_operatories_response_data['error'][0]}")
            else:
                print(f"Error: {get_operatories_response_data}")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error retrieving operatories")

        print(f"get operatories response data: {get_operatories_response_data}")

        get_operatories_response_instance = GetOperatoriesResponse(
            count=get_operatories_response_data["count"],
            data=get_operatories_response_data["data"],
        )
        return get_operatories_response_instance

    @classmethod
    def get_patients(
        cls,
        *,
        appointment_date_end: dt.date | dt.datetime | None = None,
        appointment_date_start: dt.date | dt.datetime | None = None,
        configuration: NexHealthConfig | None = None,
        date_of_birth: dt.date | None = None,
        email: str | None = None,
        foreign_id: str | None = None,
        inactive: bool = False,
        include: NexHealthIncludePatientQueryType | None = None,
        location_id: int | None = None,
        location_strict: bool | None = None,  # defaults to `False` in `NexHealth`
        name: str | None = None,
        new_patient: bool | None = None,  # defaults to `False` in `NexHealth`
        non_patient: bool = False,
        page: int | None = None,
        per_page: int = PER_PAGE,
        phone_number: str | None = None,
        raw_response: bool = False,
        subdomain: str | None = None,
        updated_since: str | None = None,
    ) -> GetPatientsResponse:
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error retrieving patients.")

        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=c_location_id,
            path="/patients",
            subdomain=c_subdomain,
        )
        url = f"{generated_url}&per_page={per_page}"
        url = f"{url}&inactive={stringify_bool(inactive)}"
        url = f"{url}&non_patient={stringify_bool(non_patient)}"

        if appointment_date_end:
            url = f"{url}&appointment_date_end={appointment_date_end}"
        if appointment_date_start:
            url = f"{url}&appointment_date_start={appointment_date_start}"
        if date_of_birth:
            url = f"{url}&date_of_birth={date_of_birth}"
        if email:
            url = f"{url}&email={email}"
        if foreign_id:
            url = f"{url}&foreign_id={foreign_id}"
        if include:
            for value in include:
                url = f"{url}&include[]={value}"
        if location_strict is not None:
            url = f"{url}&location_strict={stringify_bool(location_strict)}"
        if name:
            url = f"{url}&name={name}"
        if new_patient is not None:
            url = f"{url}&new_patient={stringify_bool(new_patient)}"
        if page:
            url = f"{url}&page={page}"
        if phone_number:
            url = f"{url}&phone_number={phone_number}"
        if updated_since:
            url = f"{url}&updated_since={updated_since}"

        fetch_patients_response = requests.get(url, headers=headers)
        fetch_patients_response_status_code = fetch_patients_response.status_code
        fetch_patients_response_data = fetch_patients_response.json()

        if fetch_patients_response_status_code != 200:
            print("Error retrieving patients")
            print(f"Response status code: {fetch_patients_response_status_code}")

            if fetch_patients_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {fetch_patients_response_data}")
                print(f"Error: {fetch_patients_response_data['error'][0]}")
            else:
                print(f"Error: {fetch_patients_response_data}")
            raise HTTPException(
                detail="Error retrieving patients",
                status_code=HTTP_400_BAD_REQUEST,
            )

        print(f"fetch patients response data: {fetch_patients_response_data}")

        patients_data: Sequence[NexHealthPatient] = fetch_patients_response_data[
            "data"
        ]["patients"]

        if raw_response:
            patients = patients_data
        else:
            patients = generate_pms_patients(patients_data)
        return GetPatientsResponse(
            count=fetch_patients_response_data["count"],
            data=patients,
        )

    @classmethod
    def get_procedures(
        cls,
        *,
        appointment_id: int | None = None,
        configuration: NexHealthConfig | None = None,
        location_id: int | None = None,
        patient_id: int | None = None,
        per_page: int = PER_PAGE,
        provider_id: int | None = None,
        subdomain: str | None = None,
        updated_after: str,
    ) -> GetProceduresResponse:
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error creating patient")

        headers = cls.generate_headers()
        url = f"{settings.nexhealth_url}/procedures"
        params = {
            "subdomain": c_subdomain,
            "location_id": c_location_id,
            "updated_after": updated_after,
            "per_page": per_page,
        }

        if appointment_id is not None:
            params["appointment_id"] = appointment_id
        if patient_id is not None:
            params["patient_id"] = patient_id
        if per_page is not None:
            params["per_page"] = per_page
        if provider_id is not None:
            params["provider_id"] = provider_id
        if updated_after is not None:
            params["updated_after"] = updated_after

        try:
            with httpx.Client() as client:
                response = client.get(url=url, params=params, headers=headers)
                response.raise_for_status()
                nex_health_get_procedures_response_data = response.json()
        except httpx.HTTPStatusError as exc:
            print(
                f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
            )
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error retrieving procedures: {exc.response.text}",
            )
        except Exception as exc:
            print(f"Unexpected error occurred: {exc}")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Unexpected error retrieving procedures: {exc}",
            )

        nex_health_get_procedures_response = GetProceduresResponse(
            count=nex_health_get_procedures_response_data["count"],
            data=nex_health_get_procedures_response_data["data"],
        )
        return nex_health_get_procedures_response

    @classmethod
    def get_providers(
        cls,
        *,
        configuration: NexHealthConfig | None = None,
        location_id: int | None = None,
        per_page: int = PER_PAGE,
        requestable: bool | None = None,
        subdomain: str | None = None,
    ):
        c_location_id, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, location_id=location_id, subdomain=subdomain
        )

        if c_location_id is None or c_subdomain is None:
            print("Error: `location_id` and/or `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error retrieving providers")

        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=c_location_id,
            path="/providers",
            subdomain=c_subdomain,
        )
        url = f"{generated_url}&per_page={per_page}"

        if requestable is not None:
            url = f"{url}&requestable={stringify_bool(requestable)}"

        get_providers_response = requests.get(url, headers=headers)
        get_providers_response_data = get_providers_response.json()
        get_providers_response_status_code = get_providers_response.status_code

        if get_providers_response_status_code != 200:
            print("Error retrieving providers")
            print(f"Response status code: {get_providers_response_status_code}")

            if get_providers_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {get_providers_response_data}")
                print(f"Error: {get_providers_response_data['error'][0]}")
            else:
                print(f"Error: {get_providers_response_data}")
            raise HTTPException(
                detail="Error retrieving providers",
                status_code=HTTP_400_BAD_REQUEST,
            )

        print(f"get providers response data: {get_providers_response_data}")

        get_providers_response_instance = GetProvidersResponse(
            count=get_providers_response_data["count"],
            data=get_providers_response_data["data"],
        )
        return get_providers_response_instance

    @classmethod
    def patch_appointment(
        cls,
        *,
        cancel: bool | None = None,
        check_in_at: str | None = None,
        configuration: NexHealthConfig | None = None,
        confirm: Literal[True] | None = None,
        id: int,
        subdomain: str | None = None,
    ) -> Appointment:
        if cancel is None and check_in_at is None and (confirm is None or not confirm):
            print("Error: no patch was action provided")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error processing appointment")

        _, c_subdomain = compute_subdomain_and_location_id(
            configuration=configuration, subdomain=subdomain
        )

        if c_subdomain is None:
            print("Error: `subdomain` missing")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error processing appointment")

        headers = cls.generate_headers(post_call=True)
        generated_url = cls.__generate_url(
            path=f"/appointments/{id}", subdomain=c_subdomain
        )

        # explicitly typed to avoid typing errors
        appt: Dict

        if cancel is not None:
            appt = {
                "cancelled": cancel,
            }
        elif confirm:
            appt = {
                "confirmed": confirm,
            }
        else:
            # because of the above validation, it can be safely assumed `check_in_at`
            # is a string
            appt = {
                "checkin_at": check_in_at,
            }

        data = {
            "appt": appt,
        }
        patch_appointment_response = requests.patch(
            generated_url, headers=headers, json=data
        )
        patch_appointment_response_data = patch_appointment_response.json()
        patch_appointment_response_status_code = patch_appointment_response.status_code

        if patch_appointment_response_status_code != 200:
            print("Error patching appointment")
            print(f"Response status code: {patch_appointment_response_status_code}")

            if patch_appointment_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {patch_appointment_response_data}")
                print(f"Error: {patch_appointment_response_data['error'][0]}")
            else:
                print(f"Error: {patch_appointment_response_data}")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error processing appointment")

        print(f"path appointment response data: {patch_appointment_response_data}")

        appointment_data: NexHealthAppointment = patch_appointment_response_data[
            "data"
        ]["appt"]
        appointment = generate_pms_appointment(appointment_data)
        return appointment

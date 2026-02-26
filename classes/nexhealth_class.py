import requests
from fastapi import HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Dict
from typing import Literal
from typing import Mapping
from typing import Sequence

# local modules
from ehr_abs_class import GetPatientsResponse
from ehr_abs_class import NexHealthConfig
from ehr_abs_class import PER_PAGE
from ehr_abs_class import PMSAbstractBaseClass
from lib.utilities import generate_pms_patients
from settings import Settings
from .nexhealth import NexHealthPatient

settings = Settings()


class NexHealthGetPatientsResponse(BaseModel):
    count: int
    data: Sequence[NexHealthPatient]


def stringify_bool(arg: bool) -> Literal["false", "true"]:
    return "true" if arg else "false"


class NexHealthSDK(PMSAbstractBaseClass):
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
            # headers["Content-Type"] = "application/json"
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
        end_time: str | None = None,
        location_id: int,
        notify_patient: bool | None = None,
        operatory_id: int,
        patient_id: int,
        provider_id: int,
        start_time: str,  # HH:mm
        subdomain: str,
    ):
        headers = cls.generate_headers(post_call=True)
        appt = {
            "operatory_id": operatory_id,
            "patient_id": patient_id,
            "provider_id": provider_id,
            "start_time": start_time,
        }
        data = {
            "appt": appt,
        }
        generated_url = cls.__generate_url(
            location_id=location_id,
            path="/appointments",
            subdomain=subdomain,
        )
        url = generated_url

        if end_time:
            appt.update({"end_time": end_time})
        if notify_patient is not None:
            url = f"{url}&notify_patient={notify_patient}"

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
            # print(f"Error: {create_appointment_response.text}")
            raise HTTPException(
                detail="Error creating appointment",
                status_code=HTTP_400_BAD_REQUEST,
            )
        print(f"Create appointment response data: {create_appointment_response_data}")
        return create_appointment_response_data["data"]

    @classmethod
    def create_appointment_type(
        cls,
        *,
        bookable_online=True,
        emr_appt_descriptor_ids: Sequence[int] = [],
        location_id: int | None = None,
        minutes=30,
        name: str,
        parent_type: (
            Literal["Institution", "Location"] | None
        ) = None,  # Defaults to "Institution" in Nexhealth
        subdomain: str,
    ):
        headers = cls.generate_headers(post_call=True)
        print(f"headers: {headers}")
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
            # data.update({"location_id": location_id})
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
            print(f"data: {data}")

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
        end_time: str,
        location_id: int,
        operatory_id: int,
        provider_id: int,
        specific_date: str | None = None,
        subdomain: str,
    ):
        headers = cls.generate_headers(post_call=True)
        generated_url = cls.__generate_url(
            location_id=location_id, path="/availabilities", subdomain=subdomain
        )
        availability = {
            "begin_time": begin_time,
            "days": days,
            "end_time": end_time,
            "operatory_id": operatory_id,
            "provider_id": provider_id,
        }
        data = {"availability": availability}

        # if active != None:
        if active is not None:
            availability.update({"active": active})
            print(f"Availability object: {availability}")
        if appointment_type_ids:
            availability.update({"appointment_type_ids": appointment_type_ids})
            print(f"Availability object: {availability}")
        if specific_date:
            availability.update({"specific_date": specific_date})
            print(f"availability: {availability}")

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
        date_of_birth: str,
        email: str,
        first_name: str,
        last_name: str,
        location_id: int,
        phone_number: str,
        provider_id: int,
        subdomain: str,
    ):
        # TO-DO: Validate whether the customer already exists
        headers = cls.generate_headers(post_call=True)
        data = {
            "patient": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "bio": {
                    "date_of_birth": date_of_birth,
                    "phone_number": phone_number,
                },
            },
            "provider": {
                "provider_id": provider_id,
            },
        }
        generated_url = cls.__generate_url(
            location_id=location_id,
            path="/patients",
            subdomain=subdomain,
        )
        create_patient_response = requests.post(
            generated_url, json=data, headers=headers
        )
        create_patient_response_status_code = create_patient_response.status_code
        create_patient_response_data = create_patient_response.json()

        if create_patient_response_status_code != 201:
            print(f"Error creating patient: {create_patient_response_data}")
            raise HTTPException(
                detail="Error creating patient",
                status_code=create_patient_response_status_code,
            )
        return create_patient_response_data["data"]["user"]

    @classmethod
    # def get_appointmen(cls, *, id: int, location_id: int, subdomain: str):
    def get_appointment(
        cls,
        *,
        id: int,
        include: Sequence[Literal["patient"]] | None = None,
        subdomain: str,
    ):
        headers = cls.generate_headers()
        # generated_url = cls.__generate_url(location_id=location_id, path=f"/appointments/{id}", subdomain=subdomain)
        generated_url = cls.__generate_url(
            path=f"/appointments/{id}", subdomain=subdomain
        )
        url = generated_url

        if include:
            for value in include:
                url = f"{url}&include[]={value}"
            print(f"url: {url}")

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
    def get_appointments(
        cls,
        *,
        end: str,
        start: str,
        configuration: NexHealthConfig,
    ):
        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=configuration.location_id,
            path="/appointments",
            subdomain=configuration.subdomain,
        )
        url = f"{generated_url}&end={end}&start={start}"
        get_appointments_response = requests.get(url, headers=headers)
        get_appointments_response_data = get_appointments_response.json()
        get_appointments_response_status_code = get_appointments_response.status_code

        if get_appointments_response_status_code != 200:
            print("Error retrieving appointments")
            print(f"Response status code: {get_appointments_response_status_code}")

            if get_appointments_response_status_code in [400, 401, 403, 404, 500]:
                print(f"Response data: {get_appointments_response_data}")
                print(f"Error: {get_appointments_response_data['error'][0]}")
            else:
                print(f"Error: {get_appointments_response_data}")
            raise HTTPException(
                detail="Error retrieving appointments",
                status_code=HTTP_400_BAD_REQUEST,
            )
        print(f"get appointments response data: {get_appointments_response_data}")
        return get_appointments_response_data["data"]

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
            # for idx, value in enumerate(include):
            #     if idx == 0:
            #         url = f"{url}?include[]={value}"
            #     else:
            #         url = f"{url}&include[]={value}"
            for value in include:
                url = f"{url}&include[]={value}"
            print(f"url: {url}")

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
    def get_operatories(
        cls,
        *,
        location_id: int,
        search_name: str | None = None,
        subdomain: str,
    ):
        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=location_id, path="/operatories", subdomain=subdomain
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
        return get_operatories_response_data["data"]

    @classmethod
    def __get_patients(
        cls,
        *,
        date_of_birth: str | None = None,
        inactive: bool = False,
        include: Sequence[Literal["adjustments"]] | None = None,
        # include: Sequence[Literal["adjustments"]] | None = None,
        non_patient: bool | None,
        location_id: int,
        per_page: int = PER_PAGE,
        phone_number: int | str | None = None,
        subdomain: str,
    ) -> NexHealthGetPatientsResponse:
        # headers = cls.generate_headers(beta_api=True)
        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=location_id,
            path="/patients",
            subdomain=subdomain,
        )
        url = f"{generated_url}&per_page={per_page}"
        url = f"{url}&inactive={stringify_bool(inactive)}"

        print(f"Headers: {headers}")

        if date_of_birth:
            url = f"{url}&date_of_birth={date_of_birth}"
        if non_patient is not None:
            url = f"{url}&non_patient={stringify_bool(non_patient)}"
        if phone_number:
            url = f"{url}&phone_number={phone_number}"
        if include is not None:
            for value in include:
                url = f"{url}&include[]={value}"
            print(f"url: {url}")

        print(f"url: {url}")

        fetch_patients_response = requests.get(url, headers=headers)
        fetch_patients_response_status_code = fetch_patients_response.status_code
        fetch_patients_response_data = fetch_patients_response.json()

        if fetch_patients_response_status_code != 200:
            print("Error retrieving patients")
            print(f"Response status code: {fetch_patients_response_status_code}")
            print(f"Error: {fetch_patients_response_data}")
            raise HTTPException(
                detail="Error retrieving patients",
                status_code=HTTP_400_BAD_REQUEST,
            )
        print(f"fetch patients response data: {fetch_patients_response_data}")
        nex_health_get_patients_response = NexHealthGetPatientsResponse(
            count=fetch_patients_response_data["count"],
            data=fetch_patients_response_data["data"]["patients"],
        )
        return nex_health_get_patients_response

    @classmethod
    def get_patients(
        cls,
        *,
        date_of_birth: str | None = None,
        inactive: bool = False,
        include: Sequence[Literal["adjustments"]] | None = ["adjustments"],
        # include: Sequence[Literal["adjustments"]] | None = None,
        non_patient: bool = False,
        per_page: int = PER_PAGE,
        phone_number: int | str | None = None,
        configuration: NexHealthConfig,
    ) -> GetPatientsResponse:
        nexhealth_get_patients_response = cls.__get_patients(
            date_of_birth=date_of_birth,
            inactive=inactive,
            include=include,
            non_patient=non_patient,
            location_id=configuration.location_id,
            per_page=per_page,
            phone_number=phone_number,
            subdomain=configuration.subdomain,
        )
        pms_patients = generate_pms_patients(nexhealth_get_patients_response.data)
        return GetPatientsResponse(
            count=nexhealth_get_patients_response.count, data=pms_patients
        )

    @classmethod
    def get_providers(
        cls,
        *,
        location_id: int,
        per_page: int = PER_PAGE,
        requestable: bool | None = None,
        subdomain: str,
    ):
        headers = cls.generate_headers()
        generated_url = cls.__generate_url(
            location_id=location_id,
            path="/providers",
            subdomain=subdomain,
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
        return get_providers_response_data["data"]

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

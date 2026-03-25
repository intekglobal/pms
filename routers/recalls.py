import datetime as dt
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Annotated
from typing import Dict
from typing import Sequence

# Local imports
from classes.nexhealth_sdk import NexHealthSDK
from classes.nexhealth import NexHealthProcedure
from classes.pms import Patient
from classes.recalls_classes import RecallsPatient
from classes.recalls_classes import RecallsPatientProviderInfo
from dependencies import validate_app_key
from ehr_abs_class import PER_PAGE
from lib.utilities.miscellaneous_utilities import calculate_age
from lib.utilities.pms_utilities import compute_new_patient_value

router = APIRouter(
    dependencies=[Depends(validate_app_key)],
    prefix="/recalls",
    tags=["recalls"],
)


@router.post("/patients-with-procedures")
async def get_patients_with_procedures(
    location_id: int,
    procedure_codes: Annotated[
        Sequence[str],
        Body(
            description="A list of procedure codes; it is possible to specify a range of procedures as well.",
            examples=[["D5730-D5760", "D6100"]],
        ),
    ],
    subdomain: str,
    end_recall_time: Annotated[
        dt.date | None,
        Body(
            description="Date value used to filter out procedures",
            examples=[dt.date(year=1990, month=8, day=29)],
        ),
    ] = None,
    exclude_with_appointments_within_last_n_days: Annotated[
        int | None,
        Body(
            description="Exclude patients that have appointments within the last N days."
        ),
    ] = None,
    exclude_with_appointments_within_next_n_days: Annotated[
        int | None,
        Body(
            description="Excludes patients that have appointments within the next N days."
        ),
    ] = None,
    max_age: Annotated[int | None, Body()] = None,
    min_age: Annotated[int | None, Body()] = None,
    per_page: int = PER_PAGE,
    start_recall_time: Annotated[
        dt.date | None,
        Body(
            description="Date value used to filter out procedures",
            examples=[dt.date(year=1990, month=8, day=29)],
        ),
    ] = None,
) -> Sequence[RecallsPatient]:
    current_page = 0
    matching_patients: list[RecallsPatient] = []
    processed_patients: int = 0
    provider_names_map: Dict[int, str] = {}
    today = dt.date.today()

    while True:
        current_page = current_page + 1
        get_patients_response = NexHealthSDK.get_patients(
            appointment_date_end=today,
            page=current_page,
            include=["procedures", "upcoming_appts"],
            location_id=location_id,
            per_page=per_page,
            raw_response=True,
            subdomain=subdomain,
        )
        get_patients_response_data = get_patients_response.data

        if not get_patients_response_data:
            # There are no more patients to process.
            # Although as mentioned above, this indicates that there are no more
            # patients left to process, in reality it is not expected to make the
            # additional call (the one with pagination/`current_page` set to a value
            # beyond what its limit should be) that returns the empty list thanks
            # to the validation below:
            # `processed_patients == get_patients_response_count`
            # should everything works as expected.
            break

        for patient in get_patients_response_data:
            # `patient` is of type `NexHealthPatient` because the usage of `raw_response=True`
            # in `NexHealthSDK`'s `get_patients`.
            # This validation is necessary to properly narrow down `patient`'s type and
            # use it without hassle from here on.
            if isinstance(patient, Patient):
                continue

            appointments = patient["appointments"]
            bio = patient["bio"]
            date_of_birth = bio["date_of_birth"]
            procedures = patient["procedures"]
            provider_id = patient["provider_id"]
            upcoming_appointments = patient["upcoming_appts"]

            # Patient exclusion validation
            if provider_id is None or not date_of_birth or not procedures:
                # Patients with no provider ID nor date of birth are considered damaged
                # and therefore ignored.
                # NOTE: this is not expected in production though.
                # Patients with no `procedures` are discarded as well given that
                # that's the intention of this endpoint.
                print(f"Damaged patient: {patient}")
                continue
            if exclude_with_appointments_within_last_n_days and appointments:
                # # Appointment past-history threshold validation: check that patient
                # # hasn't had appointments in the (forbidden?) threshold.
                # The last appointment in `appointments` is the most recent appointment
                # the patient has had.
                last_appointment = appointments[-1]
                # The time-delta value (in days) to rewind from tody, which defines the
                # past-time threshold.
                rewind_timedelta = dt.timedelta(
                    days=exclude_with_appointments_within_last_n_days
                )
                last_appointments_boundary_date = today - rewind_timedelta
                # `BaseAppointment`'s `start_time` is a date-time string, therefore if
                # has to be parsed using `datetime`
                last_appointment_start_time_datetime = dt.datetime.fromisoformat(
                    last_appointment["start_time"]
                )

                if (
                    # `last_appointment_start_time_datetime` needs to be converted to
                    # `date` in order to perform this comparison given that `last_appointments_boundary_date`
                    # (as its name suggests) is a `date`, otherwise this comparison wouldn't
                    # be possible. Note that the other way around is not possible.
                    last_appointment_start_time_datetime.date()
                    >= last_appointments_boundary_date
                ):
                    # If patient has had appointments within the set threshold (which
                    # is determined by its `start_time` value), it is ignored.
                    # Notice that because `appointments` are ascending sorted, it is
                    # enough to check most recent appoint to determine whether the patient
                    # has had appointments within the forbidden threshold.
                    continue
            if exclude_with_appointments_within_next_n_days and upcoming_appointments:
                # # Upcoming appointments's threshold validation: exclude patients with
                # # appointments inside the *forbidden* upcoming-appointments threshold.
                # NOTE: more details can be found in **Appointment past-history threshold
                # validation**.
                # `upcoming_appointments` are ascending sorted, making its first value
                # the actual first next appointment as well.
                closest_upcoming_appointment = upcoming_appointments[0]
                # The time-delta value (in days) to fast-word from today, used to define
                # forbidden upcoming-appointments threshold.
                fastforward_timedelta = dt.timedelta(
                    days=exclude_with_appointments_within_next_n_days
                )
                next_appointments_boundary_date = today + fastforward_timedelta
                closest_upcoming_appointment_start_time_datetime = (
                    dt.datetime.fromisoformat(
                        closest_upcoming_appointment["start_time"]
                    )
                )

                if (
                    closest_upcoming_appointment_start_time_datetime.date()
                    <= next_appointments_boundary_date
                ):
                    # Exclude patients with upcoming appointments within the forbidden
                    # threshold.
                    continue
            if max_age or min_age:
                # age validation
                date_of_birth_date = dt.date.fromisoformat(date_of_birth)
                age = calculate_age(date_of_birth_date)

                if (max_age and max_age < age) or (min_age and min_age > age):
                    continue

            # TODO: change to a `set` to make sure these values are unique
            matching_procedures: list[NexHealthProcedure] = []

            for procedure in procedures:
                code = procedure["code"]
                end_date = dt.date.fromisoformat(procedure["start_date"])
                start_date = dt.date.fromisoformat(procedure["end_date"])

                # Filter out procedures not within date range, if any was provided (by
                # `end_recall_time` and `start_recall_time`)
                if (end_recall_time and end_recall_time < end_date) or (
                    start_recall_time and start_recall_time > start_date
                ):
                    continue

                for procedure_code in procedure_codes:
                    # TODO: Add pattern validation for procedure codes
                    if "-" in procedure_code:
                        # procedure-code-range validation
                        start_range, end_range = procedure_code.split("-")

                        if code >= start_range and code <= end_range:
                            matching_procedures.append(procedure)
                    elif procedure_code == code:
                        matching_procedures.append(procedure)

            if matching_procedures:
                patient["procedures"] = matching_procedures

                # # Provider name functionality
                if upcoming_appointments:
                    # If there are upcoming appointments, use the name of the provider
                    # of the next upcoming appointment
                    next_upcoming_appointment = upcoming_appointments[0]
                    provider_name = next_upcoming_appointment["provider_name"]
                    recall_provider_info = RecallsPatientProviderInfo(
                        provider_id=provider_id,
                        provider_name=provider_name,
                        upcoming_appointment=True,
                    )

                    # memoized/map the provider name associated to `provider_id`.
                    provider_names_map.update(
                        {
                            next_upcoming_appointment["provider_id"]: provider_name,
                        }
                    )
                else:
                    provider_name = provider_names_map.get(provider_id, "")

                    if not provider_name:
                        # # Logic to obtain the provider name when it has not yet being
                        # # memoized.
                        provider_name_found = False

                        if appointments:
                            # Try to obtain the provider name from the patient's appointments
                            # history.
                            for appointment in appointments:
                                if provider_id == appointment["provider_id"]:
                                    provider_name = appointment["provider_name"]
                                    provider_name_found = True
                                    break
                        if not provider_name_found:
                            # If the provider name has not been found yet, try to find
                            # it from the appointments/upcoming appointments of the already
                            # retrieved patients; this is done to avoid making additional
                            # calls to `NexHealth`, and leaving that as the last resource.
                            for _patient in get_patients_response_data:
                                if isinstance(_patient, Patient):
                                    continue

                                _appointments = _patient["appointments"]
                                _upcoming_appointments = _patient["upcoming_appts"]

                                if _upcoming_appointments:
                                    # Start searching in upcoming appointments
                                    for _upcoming_appointment in _upcoming_appointments:
                                        if (
                                            provider_id
                                            == _upcoming_appointment["provider_id"]
                                        ):
                                            provider_name = _upcoming_appointment[
                                                "provider_name"
                                            ]
                                            provider_name_found = True
                                            # Exit `get_patients_response_data` loop as soon
                                            # as the provider name has been found.
                                            break
                                if _appointments:
                                    # And try in appointments history as well.
                                    for _appointment in _appointments:
                                        if provider_id == _appointment["provider_id"]:
                                            provider_name = _appointment[
                                                "provider_name"
                                            ]
                                            provider_name_found = True
                                            # End loop.
                                    break
                        if not provider_name_found:
                            # Lastly, if the provided name couldn't be found from the
                            # current patients data, then proceed to obtain it directly
                            # from `NexHealth`.
                            get_provider_response = NexHealthSDK.get_provider(
                                id=provider_id, subdomain=subdomain
                            )
                            provider_name = get_provider_response["name"]

                        # Generate the required value `provider_info` now that the
                        # value of `provider_name` has been found.
                        recall_provider_info = RecallsPatientProviderInfo(
                            provider_id=provider_id,
                            provider_name=provider_name,
                        )

                        provider_names_map.update({provider_id: provider_name})

                matching_patients.append(
                    RecallsPatient.model_validate(
                        {
                            **patient,
                            "recall_provider_info": recall_provider_info,
                            "new_patient": compute_new_patient_value(patient),
                        }
                    )
                )

        processed_patients = processed_patients + len(get_patients_response_data)
        get_patients_response_count = get_patients_response.count

        if processed_patients == get_patients_response_count:
            # All matching patients have been processed and the iteration flow can
            # be terminated.
            break
        if processed_patients > get_patients_response_count:
            # Stop and error patient processing if the the number of processed patients
            # exceed the total matched patients, which signals a problem with the code.
            print("Unexpected error processing patients")
            raise HTTPException(HTTP_400_BAD_REQUEST, "Error retrieving patients")
    return matching_patients

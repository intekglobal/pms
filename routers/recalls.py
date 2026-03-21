import datetime as dt
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from typing import Annotated
from typing import Sequence

# Local imports
from classes.nexhealth_sdk import NexHealthSDK
from classes.nexhealth import NexHealthProcedure
from classes.pms import Patient
from dependencies import validate_app_key
from ehr_abs_class import PER_PAGE
from lib.utilities.miscellaneous_utilities import calculate_age

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
    exclude_recent_contact_days: Annotated[int | None, Body()] = None,
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
) -> Sequence[Patient]:
    today = dt.date.today()
    get_patients_response = NexHealthSDK.get_patients(
        appointment_date_end=today,
        include=["procedures", "upcoming_appts"],
        location_id=location_id,
        per_page=per_page,
        # Usually when the raw, `NexHealth` response is not desired, it is not necessary
        # this value to `False` as that's its default value.
        # Because this endpoint handler currently only supports PMS `Patient` instances,
        # it is explicitly set to make sure it is not enabled unawares or by mistake.
        raw_response=False,
        subdomain=subdomain,
    )
    get_patients_response_data = get_patients_response.data
    matching_patients: list[Patient] = []

    for patient in get_patients_response_data:
        # currently there is only support fot PMS `Patient` patients
        if not isinstance(patient, Patient):
            continue

        appointments = patient.appointments
        date_of_birth = patient.date_of_birth
        procedures = patient.procedures
        upcoming_appointments = patient.upcoming_appointments

        # Skip patient with no date of birth
        # NOTE: this is not expected in production though
        if not date_of_birth:
            # TODO: add logs about missing date of birth
            continue
        # Patients with no `procedures` are discarded (given that's the intention
        # of this endpoint)
        if not procedures:
            continue
        if exclude_recent_contact_days and appointments:
            # # Appointment past-history threshold validation: check that patient
            # # hasn't had appointments in the (forbidden?) threshold.
            # The last appointment in `appointments` is the most recent appointment
            # the patient has had.
            last_appointment = appointments[-1]
            # The time-delta value (in days) to rewind from tody, which defines the
            # past-time threshold.
            timedelta = dt.timedelta(days=exclude_recent_contact_days)
            minimum_last_appointment_date = today - timedelta
            # `BaseAppointment`'s `start_time` is a date-time string, therefore if
            # has to be parsed using `datetime`
            last_appointment_start_time_datetime = dt.datetime.fromisoformat(
                last_appointment.start_time
            )

            if (
                # `last_appointment_start_time_datetime` needs to be converted to
                # `date` in order to perform this comparison given that `minimum_last_appointment_date`
                # (as its name suggests) is a `date`, otherwise this comparison wouldn't
                # be possible. Note that the other way around is not possible.
                last_appointment_start_time_datetime.date()
                >= minimum_last_appointment_date
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
                dt.datetime.fromisoformat(closest_upcoming_appointment.start_time)
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
                    start_range, end_range = procedure_code.split("-")

                    if code >= start_range and code <= end_range:
                        matching_procedures.append(procedure)
                elif procedure_code == code:
                    matching_procedures.append(procedure)

        if matching_procedures:
            patient.procedures = matching_procedures
            matching_patients.append(patient)
    return matching_patients

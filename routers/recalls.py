import datetime
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

router = APIRouter(
    dependencies=[Depends(validate_app_key)],
    prefix="/recalls",
    tags=["recalls"],
)


@router.post("/patients")
async def obtain_patients(
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
        datetime.date | None,
        Body(
            description="Date value used to filter out procedures",
            examples=[datetime.date(year=1990, month=8, day=29)],
        ),
    ] = None,
    exclude_recent_contact_days: Annotated[int | None, Body()] = None,
    max_age: Annotated[int | None, Body()] = None,
    min_age: Annotated[int | None, Body()] = None,
    per_page: int = PER_PAGE,
    start_recall_time: Annotated[
        datetime.date | None,
        Body(
            description="Date value used to filter out procedures",
            examples=[datetime.date(year=1990, month=8, day=29)],
        ),
    ] = None,
) -> Sequence[Patient]:
    get_patients_response = NexHealthSDK.get_patients(
        include=["procedures", "adjustments"],
        location_id=location_id,
        per_page=per_page,
        subdomain=subdomain,
    )
    get_patients_response_data = get_patients_response.data
    matching_patients: list[Patient] = []

    for patient in get_patients_response_data:
        if isinstance(patient, Patient):
            procedures = patient.procedures

            if procedures:
                # TODO: change to a `set` to make sure these values are unique
                matching_procedures: list[NexHealthProcedure] = []

                for procedure in procedures:
                    code = procedure["code"]
                    end_date = datetime.date.fromisoformat(procedure["start_date"])
                    start_date = datetime.date.fromisoformat(procedure["end_date"])

                    # Filter out procedures out of the date range, if any was provided
                    if (
                        # It is valid to provide no range at all
                        (end_recall_time is None and start_recall_time is None)
                        or (
                            end_recall_time
                            and start_recall_time
                            and end_recall_time >= end_date
                            and start_recall_time <= start_date
                        )
                        # It is also valid to provide only one end of the range
                        or (end_recall_time and end_recall_time >= end_date)
                        or (start_recall_time and start_recall_time <= start_date)
                    ):
                        for procedure_code in procedure_codes:
                            if "-" in procedure_code:
                                # TODO: Add pattern validation
                                start_range, end_range = procedure_code.split("-")

                                if code >= start_range and code <= end_range:
                                    matching_procedures.append(procedure)
                            elif procedure_code == code:
                                matching_procedures.append(procedure)

                if matching_procedures:
                    patient.procedures = matching_procedures
                    matching_patients.append(patient)
    return matching_patients

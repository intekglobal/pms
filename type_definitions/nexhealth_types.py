from typing import Literal
from typing import Sequence


type NexHealthIncludeAppointmentQueryValueType = Literal[
    "operatory",
    "patient",
    "procedures",
]
type NexHealthIncludeAppointmentQueryType = Sequence[
    NexHealthIncludeAppointmentQueryValueType
]
type NexHealthIncludePatientQueryValueType = Literal[
    "adjustments",
    "procedures",
    "upcoming_appts",
]
type NexHealthIncludePatientQueryType = Sequence[NexHealthIncludePatientQueryValueType]
type NexHealthParentType = Literal["Institution", "Location"]
type NexHealthSubscriptionFeatureType = Literal[
    "campaigns",
    "enterprise",
    "forms",
    "insurance_verification",
    "ledger_sync",
    "messaging",
    "online_booking",
    "payments",
    "recalls",
    "reminders",
    "reviews",
    "waitlist",
]

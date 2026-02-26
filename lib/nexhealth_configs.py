from pydantic import BaseModel
from typing import Mapping

# from typing import Sequence


class Bio(BaseModel):
    cell_phone_number: str
    date_of_birth: str
    home_phone_number: str
    phone_number: str
    work_phone_number: str


class Operatory(BaseModel):
    id: int
    name: str


class Patient(BaseModel):
    bio: Bio
    email: str
    first_name: str
    id: int
    last_name: str
    middle_name: str | None
    name: str


class Provider(BaseModel):
    id: int
    name: str


class NexhealthConfiguration(BaseModel):
    location_id: int
    operatories: Mapping[int, Operatory]
    patients: Mapping[int, Patient]
    providers: Mapping[int, Provider]
    subdomain: str


nexhealth_config = {
    "open_dental tenant ID": {
        "location ID": NexhealthConfiguration(
            location_id=341387,
            operatories={},
            patients={},
            providers={},
            subdomain="sibatel-communications",
        )
    },
    "eaglesoft tenant ID": {
        "location ID": NexhealthConfiguration(
            location_id=341396,
            subdomain="sibatel-communications",
            operatories={
                236933: {
                    "id": 236933,
                    "name": "Operatory name",
                },
            },
            patients={
                454239172: {
                    "bio": {
                        "cell_phone_number": "",
                        "date_of_birth": "1990-01-01",
                        "home_phone_number": "",
                        "phone_number": "",
                        "work_phone_number": "",
                    },
                    "email": "alex_cairns@example.com",
                    "id": 454239172,
                    "first_name": "Alex",
                    "middle_name": None,
                    "last_name": "Cairns",
                    "name": "Alex Cairns",
                },
            },
            providers={
                454098474: {
                    "id": 454098474,
                    "name": "Provider name",
                },
            },
        )
    },
}

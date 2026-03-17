import re
from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

phone_pattern = re.compile("(?:\\+\\d{1,3})?[2-9]\\d{9}")


def process_phone_number(phone_number: str, country_code: str | None = None):
    if phone_pattern.match(phone_number):
        if len(phone_number) == 10:
            return phone_number
        if country_code is not None and country_code in phone_number:
            parts = phone_number.split(country_code)
            return parts[1]
    raise HTTPException(HTTP_403_FORBIDDEN, "Phone number not allowed")

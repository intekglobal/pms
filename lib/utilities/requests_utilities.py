from fastapi import Header
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Annotated

# Local imports
from settings import settings


def validate_app_key(x_app_id: Annotated[str, Header()]):
    if x_app_id != settings.application_key:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            "You don't have access to the resource you are trying to use",
        )
    return True

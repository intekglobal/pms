from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    nexhealth_api_key: str
    nexhealth_url: str

    model_config = SettingsConfigDict(env_file=".env")

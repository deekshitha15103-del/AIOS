import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "AIOS")
    app_description: str = os.getenv(
        "APP_DESCRIPTION",
        "The Open Enterprise AI Operating System",
    )
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()
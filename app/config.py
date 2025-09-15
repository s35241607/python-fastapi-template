from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: Optional[str] = None
    schema: str = "ticket"
    secret_key: str = "your-secret-key-here"

    model_config = ConfigDict(env_file=".env")

settings = Settings()

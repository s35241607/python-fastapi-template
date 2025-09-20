from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str | None = None
    db_schema: str = "ticket"
    secret_key: str = "your-secret-key-here"

    model_config = ConfigDict(env_file=".env")


settings = Settings()

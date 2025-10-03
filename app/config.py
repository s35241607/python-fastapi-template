from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"
    debug: bool = True  # Enable debug mode to see detailed error messages
    database_url: str | None = None
    db_schema: str | None = "ticket"
    secret_key: str = "your-secret-key-here"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

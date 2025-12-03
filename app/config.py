from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Template"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True  # Enable debug mode to see detailed error messages
    DATABASE_URL: str | None = None
    DB_SCHEMA: str = "ticket"
    SECRET_KEY: str = "your-secret-key-here"

    # SMTP Settings
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025  # Default to Mailhog/Mailpit port
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_TLS: bool = False
    MAIL_FROM: str = "noreply@example.com"

    # Mail Test Mode Settings
    MAIL_TEST_MODE: bool = False
    SYSTEM_OWNER_EMAIL: list[str] = ["admin@example.com"]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

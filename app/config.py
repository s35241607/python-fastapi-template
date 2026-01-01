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

    # Logging Settings (structlog)
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_RENDER_JSON: bool = False  # True for production (Loki/Grafana)

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production

    # Mattermost Alerting
    MATTERMOST_WEBHOOK_URL: str | None = None
    MATTERMOST_CHANNEL: str | None = None  # Override default webhook channel
    ALERT_ENABLED: bool = True  # Enable/disable alerting

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

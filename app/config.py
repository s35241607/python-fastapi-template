from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"
    debug: bool = True  # Enable debug mode to see detailed error messages
    database_url: str | None = None
    db_schema: str | None = "ticket"
    secret_key: str = "your-secret-key-here"

    # Kafka Settings
    kafka_bootstrap_servers: str = "localhost:9092,localhost:9093,localhost:9094" # Comma-separated list of brokers
    kafka_notification_topic: str = "ticket_notifications"

    # SMTP Settings
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_sender: str = "noreply@example.com"
    smtp_test_mode: bool = True # In test mode, emails are logged instead of sent

    # Mattermost Settings
    mattermost_webhook_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

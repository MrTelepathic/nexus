"""Application configuration loaded from environment variables.

Uses pydantic-settings for type-safe, validated config.
Secrets are NEVER logged — only referenced by name.
"""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- App ---
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: SecretStr = Field(default=SecretStr("dev-secret-change-me"))
    app_log_level: str = "INFO"

    # --- Telegram ---
    bot_token: SecretStr
    bot_webhook_secret_token: str = ""
    bot_webhook_url: str = ""
    mini_app_url: str = "https://localhost:8000"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://nexus:nexus_dev@localhost:5432/nexus"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300

    # --- RabbitMQ ---
    rabbitmq_url: str = "amqp://nexus:nexus_dev@localhost:5672/"

    # --- MinIO / S3 ---
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "nexus-files"
    minio_secure: bool = False

    # --- AI / LLM ---
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_budget_model: str = "gpt-4o-mini"
    local_llm_url: str = "http://localhost:11434/api"

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"

    # --- TON ---
    ton_api_key: str = ""
    ton_network: str = "testnet"
    ton_escrow_address: str = ""

    # --- Sentry ---
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1

    # --- Payment ---
    stars_provider_token: str = ""
    fiat_payment_api_key: str = ""
    fiat_payment_api_secret: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def bot_token_str(self) -> str:
        return self.bot_token.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    """Singleton settings instance. Cached after first call."""
    return Settings()

from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "FastAPI Monolith Template"
    app_version: str = "1"
    debug: bool = False
    port: int = 8000
    api_prefix: str = "/api"
    shutdown_timeout: int = 10

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_monolith"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_ttl: int = 3600

    # Logging
    log_level: str = "info"
    log_json: bool = True

    # CORS
    cors_enabled: bool = True
    cors_origin: str = "http://localhost:3000"

    # Rate limiting
    throttle_limit: str = "100/minute"

    # Metrics
    metrics_enabled: bool = True

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        """Sync URL for Alembic migrations (replaces asyncpg with psycopg)."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

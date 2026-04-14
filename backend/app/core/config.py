from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://ralph:ralph_secret@db:5432/ralph_ecommerce"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Application
    debug: bool = True
    app_name: str = "Ralph E-Commerce API"
    api_v1_prefix: str = "/api/v1"

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS_ORIGINS comma-separated string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()

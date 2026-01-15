from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Authentication and JWT related settings."""

    model_config = SettingsConfigDict(
        env_prefix="auth_", env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    SECRET_KEY: str = "your-secret-key-change-in-production"
    REFRESH_TOKEN_SECRET_KEY: str = "kjnfjnfjdnjnfkjsnfsjnsjdfn"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )
    # Database
    DATABASE_URL: str
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]


# Create settings instances
settings = Settings()  # type: ignore[call-arg]
auth_settings = AuthSettings()

from pydantic_settings import BaseSettings
from typing import List


class AuthSettings(BaseSettings):
    """Authentication and JWT related settings."""
    SECRET_KEY: str = "your-secret-key-change-in-production"
    REFRESH_TOKEN_SECRET_KEY: str = "kjnfjnfjdnjnfkjsnfsjnsjdfn"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"
        env_prefix = "AUTH_"
        case_sensitive = True


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/duolingo_clone"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instances
settings = Settings()
auth_settings = AuthSettings()


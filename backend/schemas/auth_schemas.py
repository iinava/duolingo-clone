import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenType(str, Enum):
    """Token type enumeration."""

    ACCESS = "access"
    REFRESH = "refresh"


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    username: str = Field(..., min_length=3, max_length=100, examples=["johndoe"])
    password: str = Field(
        ..., min_length=8, max_length=100, examples=["securepassword123"]
    )
    full_name: Optional[str] = Field(None, max_length=255, examples=["John Doe"])

    model_config = ConfigDict()


class UserLogin(BaseModel):
    """Schema for user login - accepts email or username."""

    email_or_username: str = Field(
        ...,
        description="Email address or username",
        examples=["user@example.com", "johndoe"],
    )
    password: str = Field(..., examples=["securepassword123"])

    model_config = ConfigDict()


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(
        ..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    model_config = ConfigDict()


class TokenResponse(BaseModel):
    """Schema for token response following OAuth2 standard."""

    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    refresh_token: str = Field(
        ..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(default="bearer", examples=["bearer"])

    model_config = ConfigDict()


class UserResponse(BaseModel):
    """Schema for user response - excludes password hash."""

    id: uuid.UUID = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    email: str = Field(..., examples=["user@example.com"])
    username: str = Field(..., examples=["johndoe"])
    full_name: Optional[str] = Field(None, examples=["John Doe"])
    avatar_url: Optional[str] = Field(None, examples=[None])
    is_active: bool = Field(..., examples=[True])
    created_at: datetime = Field(..., examples=["2024-01-01T00:00:00"])
    updated_at: datetime = Field(..., examples=["2024-01-01T00:00:00"])

    model_config = ConfigDict(from_attributes=True)  # # type: ignore[call-arg]


class UserPublic(BaseModel):
    """Schema for public user profile (optional, for future use)."""

    id: uuid.UUID
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)  # type: ignore[call-arg]

"""Authentication utilities for JWT tokens and password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Any

from core.settings import auth_settings
from jose import JWTError, jwt  # type: ignore[import-untyped]
from passlib.context import CryptContext
from schemas.auth_schemas import TokenType

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


# JWT utilities
def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": TokenType.ACCESS})
    encoded_jwt = jwt.encode(
        to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({"exp": expire, "type": TokenType.REFRESH})
    encoded_jwt = jwt.encode(
        to_encode,
        auth_settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm=auth_settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str, secret: str) -> dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, secret, algorithms=[auth_settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def get_token_payload(token: str, token_type: TokenType) -> dict[str, Any]:
    secret = (
        auth_settings.SECRET_KEY
        if token_type == TokenType.ACCESS
        else auth_settings.REFRESH_TOKEN_SECRET_KEY
    )

    payload = decode_token(token, secret)

    try:
        payload_token_type = TokenType(payload["type"])
    except Exception:
        raise ValueError("Invalid token type in payload")

    if payload_token_type != token_type:
        raise ValueError("Token type mismatch")

    return payload

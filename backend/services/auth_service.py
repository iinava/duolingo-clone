import uuid
from typing import Optional

from fastapi import HTTPException, status
from models.user_models import User
from schemas.auth_schemas import TokenResponse, TokenRefresh, TokenType, UserRegister, UserLogin, UserResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth_utils import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_token_payload,
    verify_password,
)
from core.settings import auth_settings
from datetime import timedelta


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserRegister) -> User:
        """Register a new user."""
        # Check if email already exists
        existing_user = await AuthService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

        # Check if username already exists
        existing_user = await AuthService.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists",
            )

    @staticmethod
    async def register_user_with_tokens(
        db: AsyncSession, user_data: UserRegister
    ) -> TokenResponse:
        """Register a new user and return tokens."""
        user = await AuthService.register_user(db, user_data)
        return AuthService._generate_tokens_for_user(user)

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email_or_username: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by email/username and password."""
        # Try to find user by email first
        user = await AuthService.get_user_by_email(db, email_or_username)

        # If not found by email, try username
        if not user:
            user = await AuthService.get_user_by_username(db, email_or_username)

        if not user:
            return None

        # Verify password
        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def login_user(db: AsyncSession, login_data: UserLogin) -> TokenResponse:
        """Login user and return tokens."""
        user = await AuthService.authenticate_user(
            db, login_data.email_or_username, login_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
            )

        return AuthService._generate_tokens_for_user(user)

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession, refresh_data: TokenRefresh
    ) -> TokenResponse:
        """Refresh access token using refresh token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = get_token_payload(
                refresh_data.refresh_token, token_type=TokenType.REFRESH
            )
            user_id = payload.get("sub")
            if not isinstance(user_id, str) or not user_id:
                raise credentials_exception
        except ValueError:
            raise credentials_exception

        # Verify user still exists and is active
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise credentials_exception

        user = await AuthService.get_user_by_id(db, user_uuid)
        if user is None or not user.is_active:
            raise credentials_exception

        # Generate new access token
        access_token_expires = timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )

        # Return new access token (refresh token remains valid)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def get_user_profile(user: User) -> UserResponse:
        """Get user profile as UserResponse."""
        return UserResponse.model_validate(user)  # type: ignore[attr-defined]

    @staticmethod
    def _generate_tokens_for_user(user: User) -> TokenResponse:
        """Generate access and refresh tokens for a user."""
        access_token_expires = timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


# Backward compatibility - export functions for existing code
async def register_user(db: AsyncSession, user_data: UserRegister) -> User:
    """Register a new user."""
    return await AuthService.register_user(db, user_data)


async def authenticate_user(
    db: AsyncSession, email_or_username: str, password: str
) -> Optional[User]:
    """Authenticate a user by email/username and password."""
    return await AuthService.authenticate_user(db, email_or_username, password)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    return await AuthService.get_user_by_email(db, email)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    return await AuthService.get_user_by_username(db, username)


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID."""
    return await AuthService.get_user_by_id(db, user_id)

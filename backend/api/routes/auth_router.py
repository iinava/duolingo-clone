from typing import Annotated

from api.deps import get_current_active_user
from db.deps import get_db
from fastapi import APIRouter, Depends, status
from models.user_models import User
from schemas.auth_schemas import (
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    """Register a new user."""
    return await AuthService.register_user_with_tokens(db, user_data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    """Login with email/username and password."""
    return await AuthService.login_user(db, login_data)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: TokenRefresh, db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    """Refresh access token using refresh token."""
    return await AuthService.refresh_access_token(db, refresh_data)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current authenticated user's profile."""
    return await AuthService.get_user_profile(current_user)

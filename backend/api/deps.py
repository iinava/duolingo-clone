import uuid
from typing import Annotated

from db.deps import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.user_models import User
from schemas.auth_schemas import TokenType
from services.auth_service import get_user_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth_utils import get_token_payload

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user from access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = get_token_payload(token, token_type=TokenType.ACCESS)
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise credentials_exception
    except (ValueError, KeyError):
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception

    user = await get_user_by_id(db, user_uuid)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user - ensures user is not disabled."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user

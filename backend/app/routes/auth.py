import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserProfileUpdate,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    register_user,
    request_password_reset,
    reset_password,
    update_user_profile,
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(db, payload.name, payload.email, payload.password)
        auth_result = authenticate_user(db, payload.email, payload.password)
        return TokenResponse(
            access_token=auth_result["access_token"],
            user=UserResponse.model_validate(user),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return JWT token",
)
async def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    try:
        auth_result = authenticate_user(db, payload.email, payload.password)
        return TokenResponse(
            access_token=auth_result["access_token"],
            user=UserResponse.model_validate(auth_result["user"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to an internal error",
        )


@router.post(
    "/forgot-password",
    summary="Request a password reset token",
)
async def forgot_password(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    try:
        result = request_password_reset(db, payload.email)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed due to an internal error",
        )


@router.post(
    "/reset-password",
    summary="Reset password using a valid reset token",
)
async def reset_password_endpoint(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    try:
        result = reset_password(db, payload.token, payload.new_password)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed due to an internal error",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user's profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update the current user's profile",
)
async def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated = update_user_profile(
            db,
            current_user,
            name=payload.name,
            profile_picture=payload.profile_picture,
        )
        return UserResponse.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed due to an internal error",
        )

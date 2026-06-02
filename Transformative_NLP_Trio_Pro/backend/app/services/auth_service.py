import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import PasswordResetToken, User
from app.utils.auth import (
    create_access_token,
    generate_reset_token,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)


def register_user(db: Session, name: str, email: str, password: str) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Registered new user: {user.email}")
    return user


def authenticate_user(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    logger.info(f"User authenticated: {user.email}")
    return {"access_token": access_token, "user": user}


def request_password_reset(db: Session, email: str) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}
    reset_token = generate_reset_token()
    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    db.add(token_record)
    db.commit()
    logger.info(f"Password reset requested for: {email}")
    return {"message": "If the email exists, a reset link has been sent"}


def reset_password(db: Session, token: str, new_password: str) -> dict:
    token_record = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == token, PasswordResetToken.used == False)
        .first()
    )
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    if token_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.password_hash = hash_password(new_password)
    token_record.used = True
    db.commit()
    logger.info(f"Password reset for user: {user.email}")
    return {"message": "Password has been reset successfully"}


def update_user_profile(
    db: Session, user: User, name: Optional[str] = None, profile_picture: Optional[str] = None
) -> User:
    if name is not None:
        user.name = name
    if profile_picture is not None:
        user.profile_picture = profile_picture
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    logger.info(f"Profile updated for user: {user.email}")
    return user

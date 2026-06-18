import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Float,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.database import Base


def _utcnow():
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_picture = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    is_active = Column(Boolean, default=True)

    processing_history = relationship(
        "ProcessingHistory", back_populates="user", cascade="all, delete-orphan"
    )
    analytics_logs = relationship(
        "AnalyticsLog", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )


class ProcessingHistory(Base):
    __tablename__ = "processing_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    audio_filename = Column(String(512), nullable=True)
    audio_path = Column(String(1024), nullable=True)
    recognized_text = Column(Text, nullable=True)
    summary_text = Column(Text, nullable=True)
    translated_text = Column(Text, nullable=True)
    target_language = Column(String(10), nullable=True)
    source_language = Column(String(10), nullable=True)
    summary_mode = Column(String(20), nullable=True)
    audio_output_path = Column(String(1024), nullable=True)
    sentiment = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    meeting_minutes = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="processing_history")


class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    operation_type = Column(String(50), nullable=False)
    source_language = Column(String(10), nullable=True)
    target_language = Column(String(10), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="success")
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="analytics_logs")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = Column(String(512), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    user = relationship("User", back_populates="password_reset_tokens")

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.database.models import ProcessingHistory

logger = logging.getLogger(__name__)


def save_processing_record(
    db: Session,
    user_id: uuid.UUID,
    data: Dict[str, Any],
) -> ProcessingHistory:
    record = ProcessingHistory(
        id=uuid.uuid4(),
        user_id=user_id,
        audio_filename=data.get("audio_filename"),
        audio_path=data.get("audio_path"),
        recognized_text=data.get("recognized_text"),
        summary_text=data.get("summary_text"),
        translated_text=data.get("translated_text"),
        target_language=data.get("target_language"),
        source_language=data.get("source_language"),
        summary_mode=data.get("summary_mode"),
        audio_output_path=data.get("audio_output_path"),
        sentiment=data.get("sentiment"),
        keywords=data.get("keywords"),
        meeting_minutes=data.get("meeting_minutes"),
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Processing record saved: %s for user %s", record.id, user_id)
    return record


def get_user_history(
    db: Session,
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> List[ProcessingHistory]:
    records = (
        db.query(ProcessingHistory)
        .filter(ProcessingHistory.user_id == user_id)
        .order_by(desc(ProcessingHistory.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return records


def get_user_history_count(db: Session, user_id: uuid.UUID) -> int:
    return (
        db.query(ProcessingHistory)
        .filter(ProcessingHistory.user_id == user_id)
        .count()
    )


def get_history_by_id(
    db: Session,
    history_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[ProcessingHistory]:
    return (
        db.query(ProcessingHistory)
        .filter(
            and_(
                ProcessingHistory.id == history_id,
                ProcessingHistory.user_id == user_id,
            )
        )
        .first()
    )


def delete_history_record(
    db: Session,
    history_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    record = get_history_by_id(db, history_id, user_id)
    if not record:
        return False

    db.delete(record)
    db.commit()
    logger.info("Processing record deleted: %s", history_id)
    return True


def search_history(
    db: Session,
    user_id: uuid.UUID,
    search_term: str,
    limit: int = 20,
) -> List[ProcessingHistory]:
    term = f"%{search_term}%"
    records = (
        db.query(ProcessingHistory)
        .filter(
            and_(
                ProcessingHistory.user_id == user_id,
                or_(
                    ProcessingHistory.recognized_text.ilike(term),
                    ProcessingHistory.summary_text.ilike(term),
                    ProcessingHistory.translated_text.ilike(term),
                    ProcessingHistory.audio_filename.ilike(term),
                ),
            )
        )
        .order_by(desc(ProcessingHistory.created_at))
        .limit(limit)
        .all()
    )
    return records


def get_recent_items(
    db: Session,
    user_id: uuid.UUID,
    count: int = 5,
) -> List[ProcessingHistory]:
    records = (
        db.query(ProcessingHistory)
        .filter(ProcessingHistory.user_id == user_id)
        .order_by(desc(ProcessingHistory.created_at))
        .limit(count)
        .all()
    )
    return records

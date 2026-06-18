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
    user: Any,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    user_id = user.id if hasattr(user, "id") else user
    offset = (page - 1) * limit
    
    total = (
        db.query(ProcessingHistory)
        .filter(ProcessingHistory.user_id == user_id)
        .count()
    )
    
    records = (
        db.query(ProcessingHistory)
        .filter(ProcessingHistory.user_id == user_id)
        .order_by(desc(ProcessingHistory.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    import math
    pages = math.ceil(total / limit) if limit > 0 else 0
    
    return {
        "items": records,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


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


def get_history_item(
    db: Session,
    user: Any,
    history_id: uuid.UUID,
) -> ProcessingHistory:
    from fastapi import HTTPException
    user_id = user.id if hasattr(user, "id") else user
    item = get_history_by_id(db, history_id, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="History record not found")
    return item


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


def delete_history_item(
    db: Session,
    user: Any,
    history_id: uuid.UUID,
) -> dict:
    user_id = user.id if hasattr(user, "id") else user
    success = delete_history_record(db, history_id, user_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="History record not found")
    return {"status": "success", "message": "History record deleted successfully"}


def search_history(
    db: Session,
    user: Any,
    search_term: str,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    user_id = user.id if hasattr(user, "id") else user
    offset = (page - 1) * limit
    term = f"%{search_term}%"
    
    query = (
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
    )
    
    total = query.count()
    
    records = (
        query.order_by(desc(ProcessingHistory.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    import math
    pages = math.ceil(total / limit) if limit > 0 else 0
    
    return {
        "items": records,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


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


def get_recent_history(
    db: Session,
    user: Any,
    limit: int = 10,
) -> Dict[str, Any]:
    user_id = user.id if hasattr(user, "id") else user
    records = get_recent_items(db, user_id, limit)
    total = (
        db.query(ProcessingHistory)
        .filter(ProcessingHistory.user_id == user_id)
        .count()
    )
    return {
        "items": records,
        "total": total,
    }

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, cast, Date

from app.database.models import AnalyticsLog

logger = logging.getLogger(__name__)

VALID_OPERATIONS = {
    "speech_to_text", "summarization", "translation",
    "text_to_speech", "sentiment_analysis", "keyword_extraction",
    "question_answering", "meeting_minutes", "pdf_report",
}


def log_operation(
    db: Session,
    user_id: uuid.UUID,
    operation_type: str,
    data: Optional[Dict[str, Any]] = None,
) -> AnalyticsLog:
    if operation_type not in VALID_OPERATIONS:
        logger.warning("Unknown operation type: %s", operation_type)

    event = AnalyticsLog(
        id=uuid.uuid4(),
        user_id=user_id,
        operation_type=operation_type,
        source_language=data.get("source_language") if data else None,
        target_language=data.get("target_language") if data else None,
        duration_ms=data.get("duration_ms") if data else None,
        status=data.get("status", "success") if data else "success",
        created_at=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info("Analytics event logged: %s for user %s", operation_type, user_id)
    return event


def get_user_analytics(db: Session, user: Any) -> Dict[str, Any]:
    user_id = user.id if hasattr(user, "id") else user
    total_ops = (
        db.query(func.count(AnalyticsLog.id))
        .filter(AnalyticsLog.user_id == user_id)
        .scalar()
    )

    op_counts = (
        db.query(AnalyticsLog.operation_type, func.count(AnalyticsLog.id))
        .filter(AnalyticsLog.user_id == user_id)
        .group_by(AnalyticsLog.operation_type)
        .all()
    )

    operations = {op: count for op, count in op_counts}

    first_activity = (
        db.query(func.min(AnalyticsLog.created_at))
        .filter(AnalyticsLog.user_id == user_id)
        .scalar()
    )
    last_activity = (
        db.query(func.max(AnalyticsLog.created_at))
        .filter(AnalyticsLog.user_id == user_id)
        .scalar()
    )

    success_count = (
        db.query(func.count(AnalyticsLog.id))
        .filter(
            and_(
                AnalyticsLog.user_id == user_id,
                AnalyticsLog.status == "success",
            )
        )
        .scalar()
    )

    sources = (
        db.query(AnalyticsLog.source_language, func.count(AnalyticsLog.id))
        .filter(
            and_(
                AnalyticsLog.user_id == user_id,
                AnalyticsLog.source_language.isnot(None),
            )
        )
        .group_by(AnalyticsLog.source_language)
        .order_by(func.count(AnalyticsLog.id).desc())
        .limit(10)
        .all()
    )

    targets = (
        db.query(AnalyticsLog.target_language, func.count(AnalyticsLog.id))
        .filter(
            and_(
                AnalyticsLog.user_id == user_id,
                AnalyticsLog.target_language.isnot(None),
            )
        )
        .group_by(AnalyticsLog.target_language)
        .order_by(func.count(AnalyticsLog.id).desc())
        .limit(10)
        .all()
    )

    return {
        "total_operations": total_ops or 0,
        "operations_by_type": operations,
        "success_rate": round((success_count or 0) / max(total_ops or 1, 1) * 100, 1),
        "first_activity": first_activity.isoformat() if first_activity else None,
        "last_activity": last_activity.isoformat() if last_activity else None,
        "top_source_languages": [{"language": lang, "count": count} for lang, count in sources],
        "top_target_languages": [{"language": lang, "count": count} for lang, count in targets],
    }


def get_admin_analytics(db: Session, user: Any = None) -> Dict[str, Any]:
    total_users = (
        db.query(func.count(func.distinct(AnalyticsLog.user_id))).scalar()
    )

    total_ops = db.query(func.count(AnalyticsLog.id)).scalar()

    op_counts = (
        db.query(AnalyticsLog.operation_type, func.count(AnalyticsLog.id))
        .group_by(AnalyticsLog.operation_type)
        .order_by(func.count(AnalyticsLog.id).desc())
        .all()
    )

    today = datetime.utcnow().date()
    ops_today = (
        db.query(func.count(AnalyticsLog.id))
        .filter(cast(AnalyticsLog.created_at, Date) == today)
        .scalar()
    )

    success_count = (
        db.query(func.count(AnalyticsLog.id))
        .filter(AnalyticsLog.status == "success")
        .scalar()
    )

    active_users_7d = (
        db.query(func.count(func.distinct(AnalyticsLog.user_id)))
        .filter(
            AnalyticsLog.created_at >= datetime.utcnow() - timedelta(days=7)
        )
        .scalar()
    )

    return {
        "total_unique_users": total_users or 0,
        "total_operations": total_ops or 0,
        "operations_today": ops_today or 0,
        "active_users_7d": active_users_7d or 0,
        "overall_success_rate": round(
            (success_count or 0) / max(total_ops or 1, 1) * 100, 1
        ),
        "operations_by_type": {op: count for op, count in op_counts},
    }


def get_daily_breakdown(db: Session, user: Any, days: int = 30) -> List[Dict[str, Any]]:
    user_id = user.id if hasattr(user, "id") else user
    cutoff = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(
            cast(AnalyticsLog.created_at, Date).label("day"),
            func.count(AnalyticsLog.id).label("count"),
        )
        .filter(
            and_(
                AnalyticsLog.user_id == user_id,
                AnalyticsLog.created_at >= cutoff,
            )
        )
        .group_by(cast(AnalyticsLog.created_at, Date))
        .order_by(cast(AnalyticsLog.created_at, Date).asc())
        .all()
    )

    return [
        {"date": str(row.day), "count": row.count}
        for row in results
    ]


def get_language_stats(db: Session, user: Any) -> Dict[str, Any]:
    user_id = user.id if hasattr(user, "id") else user
    sources = (
        db.query(AnalyticsLog.source_language, func.count(AnalyticsLog.id))
        .filter(
            and_(
                AnalyticsLog.user_id == user_id,
                AnalyticsLog.source_language.isnot(None),
            )
        )
        .group_by(AnalyticsLog.source_language)
        .order_by(func.count(AnalyticsLog.id).desc())
        .limit(20)
        .all()
    )

    targets = (
        db.query(AnalyticsLog.target_language, func.count(AnalyticsLog.id))
        .filter(
            and_(
                AnalyticsLog.user_id == user_id,
                AnalyticsLog.target_language.isnot(None),
            )
        )
        .group_by(AnalyticsLog.target_language)
        .order_by(func.count(AnalyticsLog.id).desc())
        .limit(20)
        .all()
    )

    return {
        "source_languages": [
            {"language": lang, "count": count} for lang, count in sources
        ],
        "target_languages": [
            {"language": lang, "count": count} for lang, count in targets
        ],
    }


def get_operation_breakdown(db: Session, user: Any) -> List[Dict[str, Any]]:
    user_id = user.id if hasattr(user, "id") else user
    results = (
        db.query(
            AnalyticsLog.operation_type,
            func.count(AnalyticsLog.id).label("count"),
        )
        .filter(AnalyticsLog.user_id == user_id)
        .group_by(AnalyticsLog.operation_type)
        .order_by(func.count(AnalyticsLog.id).desc())
        .all()
    )

    return [
        {
            "operation": op,
            "count": count,
        }
        for op, count in results
    ]

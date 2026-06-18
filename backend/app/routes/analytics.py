import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.services.analytics_service import (
    get_admin_analytics,
    get_daily_breakdown,
    get_language_stats,
    get_operation_breakdown,
    get_user_analytics,
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get(
    "/user",
    summary="Get analytics for the current authenticated user",
)
async def user_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_user_analytics(db, current_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user analytics",
        )


@router.get(
    "/admin",
    summary="Get global admin-level analytics",
)
async def admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_admin_analytics(db, current_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin analytics",
        )


@router.get(
    "/daily",
    summary="Get daily activity breakdown for the current user",
)
async def daily_breakdown(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_daily_breakdown(db, current_user, days=days)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily analytics",
        )


@router.get(
    "/languages",
    summary="Get language usage statistics for the current user",
)
async def language_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_language_stats(db, current_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Language stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve language statistics",
        )


@router.get(
    "/operations",
    summary="Get operation type breakdown for the current user",
)
async def operation_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_operation_breakdown(db, current_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Operations analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve operation breakdown",
        )

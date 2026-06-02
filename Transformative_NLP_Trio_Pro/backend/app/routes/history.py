import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import HistoryResponse
from app.services.history_service import (
    delete_history_item,
    get_history_item,
    get_recent_history,
    get_user_history,
    search_history,
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get(
    "/",
    summary="Get paginated processing history for the current user",
)
async def list_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = get_user_history(db, current_user, page=page, limit=limit)
        return {
            "items": [HistoryResponse.model_validate(item) for item in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history",
        )


@router.get(
    "/{history_id}",
    response_model=HistoryResponse,
    summary="Get a single history record by ID",
)
async def get_history(
    history_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        item = get_history_item(db, current_user, history_id)
        return HistoryResponse.model_validate(item)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get history item error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history record",
        )


@router.delete(
    "/{history_id}",
    summary="Delete a history record",
)
async def delete_history(
    history_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_history_item(db, current_user, history_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete history record",
        )


@router.get(
    "/search",
    summary="Search processing history by text content",
)
async def search_history_endpoint(
    q: str = Query(..., min_length=1, description="Search query text"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = search_history(db, current_user, q, page=page, limit=limit)
        return {
            "items": [HistoryResponse.model_validate(item) for item in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search history",
        )


@router.get(
    "/recent",
    summary="Get the 10 most recent history items",
)
async def get_recent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = get_recent_history(db, current_user, limit=10)
        return {
            "items": [HistoryResponse.model_validate(item) for item in result["items"]],
            "total": result["total"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recent history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent history",
        )

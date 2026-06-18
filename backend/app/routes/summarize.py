import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import (
    BatchSummarizeRequest,
    SummarizeRequest,
    SummarizeResponse,
)
from app.services.summarize_service import (
    get_available_modes,
    summarize_batch,
    summarize_text,
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/summarize", tags=["Summarization"])


@router.post(
    "/",
    response_model=SummarizeResponse,
    summary="Summarize a single text with the specified mode",
)
async def summarize(
    payload: SummarizeRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = summarize_text(payload.text, mode=payload.mode)
        return SummarizeResponse(
            summary=result["summary"],
            original_length=result["original_length"],
            summary_length=result["summary_length"],
            mode=result["mode"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Summarization failed due to an internal error",
        )


@router.post(
    "/batch",
    summary="Summarize multiple texts in a single request",
)
async def batch_summarize(
    payload: BatchSummarizeRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = summarize_batch(payload.texts, mode=payload.mode)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch summarization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch summarization failed due to an internal error",
        )


@router.get(
    "/modes",
    summary="Get available summarization modes",
)
async def list_modes(
    current_user: User = Depends(get_current_user),
):
    try:
        return get_available_modes()
    except Exception as e:
        logger.error(f"Get modes error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve summarization modes",
        )

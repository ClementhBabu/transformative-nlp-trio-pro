import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import (
    KeyphraseRequest,
    KeywordRequest,
    KeywordResponse,
)
from app.services.keywords_service import extract_keyphrases, extract_keywords
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/keywords", tags=["Keyword Extraction"])


@router.post(
    "/extract",
    response_model=KeywordResponse,
    summary="Extract keywords from provided text",
)
async def extract(
    payload: KeywordRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = extract_keywords(payload.text, num_keywords=payload.num_keywords)
        return KeywordResponse(
            keywords=result["keywords"],
            score=result.get("score"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Keyword extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keyword extraction failed due to an internal error",
        )


@router.post(
    "/keyphrases",
    summary="Extract keyphrases from provided text",
)
async def keyphrases(
    payload: KeyphraseRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = extract_keyphrases(payload.text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Keyphrase extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keyphrase extraction failed due to an internal error",
        )

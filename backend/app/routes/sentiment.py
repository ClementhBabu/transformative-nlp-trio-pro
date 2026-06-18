import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import (
    BatchSentimentRequest,
    SentimentRequest,
    SentimentResponse,
)
from app.services.sentiment_service import analyze_sentiment, batch_analyze_sentiment
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])


@router.post(
    "/analyze",
    response_model=SentimentResponse,
    summary="Analyze the sentiment of provided text",
)
async def analyze(
    payload: SentimentRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = analyze_sentiment(payload.text)
        return SentimentResponse(
            polarity=result["polarity"],
            subjectivity=result["subjectivity"],
            classification=result["classification"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sentiment analysis failed due to an internal error",
        )


@router.post(
    "/batch",
    summary="Analyze sentiment for multiple texts",
)
async def batch_analyze(
    payload: BatchSentimentRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return batch_analyze_sentiment(payload.texts)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch sentiment analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch sentiment analysis failed due to an internal error",
        )

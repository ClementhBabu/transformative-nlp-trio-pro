import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import TranslateRequest, TranslateResponse
from app.services.translate_service import (
    detect_language,
    get_supported_languages,
    translate_text,
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/translate", tags=["Translation"])


@router.post(
    "/",
    response_model=TranslateResponse,
    summary="Translate text from source language to target language",
)
async def translate(
    payload: TranslateRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = translate_text(
            payload.text,
            source_lang=payload.source_lang,
            target_lang=payload.target_lang,
        )
        return TranslateResponse(
            translated_text=result["translated_text"],
            source_lang=result["source_lang"],
            target_lang=result["target_lang"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation failed due to an internal error",
        )


@router.get(
    "/languages",
    summary="Get the list of supported translation languages",
)
async def list_languages(
    current_user: User = Depends(get_current_user),
):
    try:
        return get_supported_languages()
    except Exception as e:
        logger.error(f"Get languages error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supported languages",
        )


@router.post(
    "/detect",
    summary="Detect the language of provided text",
)
async def detect_text_language(
    text: str,
    current_user: User = Depends(get_current_user),
):
    try:
        result = detect_language(text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language detection failed due to an internal error",
        )

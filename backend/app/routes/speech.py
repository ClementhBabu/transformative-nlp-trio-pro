import logging
import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import AudioUploadResponse, SpeechToTextResponse
from app.services.speech_service import (
    detect_language,
    get_task_status,
    speech_to_text,
    upload_audio,
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/speech", tags=["Speech Processing"])


@router.post(
    "/upload",
    response_model=AudioUploadResponse,
    summary="Upload an audio file for processing",
)
async def upload_audio_file(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, M4A, OGG, WebM)"),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await upload_audio(file)
        return AudioUploadResponse(
            filename=result["filename"],
            file_path=result["file_path"],
            duration_seconds=result.get("duration_seconds"),
            file_size_bytes=result.get("file_size_bytes"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audio upload failed due to an internal error",
        )


@router.post(
    "/speech-to-text",
    response_model=SpeechToTextResponse,
    summary="Convert uploaded audio to text using speech recognition",
)
async def speech_to_text_endpoint(
    file: UploadFile = File(None, description="Audio file to transcribe"),
    file_path: str = Form(None, description="Path to previously uploaded audio file"),
    language: str = Form(None, description="Source language code (e.g., en, es, fr)"),
    current_user: User = Depends(get_current_user),
):
    if not file and not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file upload or file_path must be provided",
        )
    try:
        result = await speech_to_text(
            file_path=file_path,
            upload_file=file,
            language=language,
        )
        return SpeechToTextResponse(
            text=result["text"],
            language=result.get("language"),
            duration_seconds=result.get("duration_seconds"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Speech-to-text processing failed due to an internal error",
        )


@router.post(
    "/detect-language",
    summary="Detect spoken language from an audio file",
)
async def detect_language_endpoint(
    file: UploadFile = File(None, description="Audio file for language detection"),
    file_path: str = Form(None, description="Path to previously uploaded audio file"),
    current_user: User = Depends(get_current_user),
):
    if not file and not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file upload or file_path must be provided",
        )
    try:
        result = await detect_language(
            file_path=file_path,
            upload_file=file,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language detection failed due to an internal error",
        )


@router.get(
    "/status/{task_id}",
    summary="Check the status of a speech processing task",
)
async def check_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        return get_task_status(task_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status",
        )

import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import TTSRequest, TTSResponse
from app.services.tts_service import generate_speech, get_audio_path, get_voices
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["Text-to-Speech"])


@router.post(
    "/generate",
    response_model=TTSResponse,
    summary="Generate speech audio from text input",
)
async def generate(
    payload: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = generate_speech(
            payload.text,
            language=payload.language,
            gender=payload.gender or "female",
        )
        return TTSResponse(
            audio_url=result["audio_url"],
            format=result.get("format", "mp3"),
            duration_seconds=result.get("duration_seconds"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TTS generation failed due to an internal error",
        )


@router.get(
    "/voices",
    summary="Get available TTS voice options",
)
async def list_voices(
    language: Optional[str] = Query(None, description="Filter voices by language code"),
    gender: Optional[str] = Query(None, description="Filter voices by gender (male/female)"),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_voices(language=language, gender=gender)
    except Exception as e:
        logger.error(f"Get voices error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve voice options",
        )


@router.get(
    "/download/{filename}",
    summary="Download a generated audio file",
)
async def download_audio(
    filename: str,
):
    try:
        file_path = get_audio_path(filename)
        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download audio file",
        )


@router.get(
    "/stream/{filename}",
    summary="Stream an audio file for playback",
)
async def stream_audio(
    filename: str,
):
    try:
        file_path = get_audio_path(filename)
        file_size = os.path.getsize(file_path)

        def iterfile():
            chunk_size = 1024 * 64
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        return StreamingResponse(
            iterfile(),
            media_type="audio/mpeg",
            headers={
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio streaming error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream audio file",
        )


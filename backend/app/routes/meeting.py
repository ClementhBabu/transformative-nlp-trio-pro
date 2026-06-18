import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import MeetingMinutesRequest, MeetingMinutesResponse
from app.services.meeting_service import (
    generate_minutes,
    generate_minutes_from_audio,
    get_minutes,
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/meeting", tags=["Meeting Minutes"])


@router.post(
    "/generate",
    response_model=MeetingMinutesResponse,
    summary="Generate meeting minutes from a transcript text",
)
async def generate_minutes_endpoint(
    payload: MeetingMinutesRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = generate_minutes(payload.text)
        return MeetingMinutesResponse(
            title=result.get("title"),
            date=result.get("date"),
            attendees=result.get("attendees"),
            agenda=result.get("agenda"),
            discussion_points=result.get("discussion_points"),
            action_items=result.get("action_items"),
            decisions=result.get("decisions"),
            next_meeting=result.get("next_meeting"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Meeting minutes generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Meeting minutes generation failed due to an internal error",
        )


@router.post(
    "/from-audio",
    summary="Generate meeting minutes directly from an audio file",
)
async def generate_from_audio(
    file: UploadFile = File(..., description="Audio recording of the meeting"),
    source_lang: Optional[str] = Form(None, description="Source language of the audio"),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await generate_minutes_from_audio(file, source_lang=source_lang)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Meeting minutes from audio error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Meeting minutes generation from audio failed",
        )


@router.get(
    "/{minutes_id}",
    summary="Get previously generated meeting minutes by ID",
)
async def get_saved_minutes(
    minutes_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        return get_minutes(minutes_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get meeting minutes error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve meeting minutes",
        )

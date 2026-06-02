import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import ProcessingPipelineResponse
from app.services.pipeline_service import get_pipeline_status, process_pipeline
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pipeline", tags=["Processing Pipeline"])


@router.post(
    "/process",
    response_model=ProcessingPipelineResponse,
    summary="Run the complete NLP pipeline on an audio file",
    description=(
        "Full pipeline: Upload audio -> Speech-to-Text -> Summarize -> "
        "Translate -> TTS -> Keywords -> Sentiment -> Meeting Minutes -> Save to History"
    ),
)
async def process(
    file: UploadFile = File(..., description="Audio file to process"),
    target_lang: Optional[str] = Form(None, description="Target language for translation"),
    source_lang: Optional[str] = Form(None, description="Source language for STT"),
    mode: str = Form("medium", description="Summarization mode (short/medium/detailed/bullet)"),
    generate_tts: bool = Form(True, description="Whether to generate TTS output audio"),
    generate_report: bool = Form(False, description="Whether to generate a PDF report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await process_pipeline(
            db=db,
            user=current_user,
            upload_file=file,
            mode=mode,
            target_lang=target_lang,
            source_lang=source_lang,
            generate_tts=generate_tts,
            generate_report_flag=generate_report,
        )
        return ProcessingPipelineResponse(
            history_id=result["history_id"],
            recognized_text=result.get("recognized_text"),
            summary_text=result.get("summary_text"),
            translated_text=result.get("translated_text"),
            sentiment=result.get("sentiment"),
            keywords=result.get("keywords"),
            meeting_minutes=result.get("meeting_minutes"),
            audio_output_url=result.get("audio_output_url"),
            report_url=result.get("report_url"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pipeline processing failed due to an internal error",
        )


@router.get(
    "/status/{pipeline_id}",
    summary="Check the status of a pipeline execution",
)
async def check_pipeline_status(
    pipeline_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        return get_pipeline_status(pipeline_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pipeline status",
        )

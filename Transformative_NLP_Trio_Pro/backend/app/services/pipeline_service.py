import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.models import ProcessingHistory, User
from app.services.speech_service import speech_to_text
from app.services.summarize_service import summarize_text
from app.services.translate_service import translate_text
from app.services.tts_service import generate_speech
from app.services.sentiment_service import analyze_sentiment
from app.services.keywords_service import extract_keywords
from app.services.meeting_service import generate_minutes
from app.services.report_service import generate_report

logger = logging.getLogger(__name__)

_pipeline_store: dict = {}


async def process_pipeline(
    db: Session,
    user: User,
    upload_file: UploadFile,
    mode: str = "medium",
    target_lang: Optional[str] = None,
    source_lang: Optional[str] = None,
    generate_tts: bool = True,
    generate_report_flag: bool = False,
) -> dict:
    pipeline_id = str(uuid.uuid4())
    _pipeline_store[pipeline_id] = {
        "status": "processing",
        "steps_completed": [],
    }

    logger.info(
        f"Pipeline {pipeline_id} started for user {user.id}, "
        f"mode={mode}, target_lang={target_lang}"
    )

    response = {"history_id": None, "recognized_text": None, "summary_text": None,
                "translated_text": None, "sentiment": None, "keywords": None,
                "meeting_minutes": None, "audio_output_url": None, "report_url": None}

    try:
        # Step 1: Speech-to-Text
        stt_result = await speech_to_text(upload_file=upload_file, language=source_lang)
        recognized_text = stt_result["text"]
        detected_language = stt_result.get("language", source_lang)
        response["recognized_text"] = recognized_text
        _pipeline_store[pipeline_id]["steps_completed"].append("speech_to_text")

        # Step 2: Summarize
        if recognized_text and recognized_text.strip():
            summary_result = summarize_text(recognized_text, mode=mode)
            summary_text = summary_result["summary"]
            response["summary_text"] = summary_text
        else:
            summary_text = None
        _pipeline_store[pipeline_id]["steps_completed"].append("summarize")

        # Step 3: Translate (if target language specified)
        translated_text = None
        if target_lang and recognized_text:
            translation_result = translate_text(
                recognized_text,
                source_lang=detected_language or "auto",
                target_lang=target_lang,
            )
            translated_text = translation_result["translated_text"]
            response["translated_text"] = translated_text
        _pipeline_store[pipeline_id]["steps_completed"].append("translate")

        # Step 4: Sentiment Analysis
        if recognized_text:
            try:
                sentiment_result = analyze_sentiment(recognized_text)
                response["sentiment"] = sentiment_result
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        _pipeline_store[pipeline_id]["steps_completed"].append("sentiment")

        # Step 5: Keyword Extraction
        if recognized_text:
            try:
                keyword_result = extract_keywords(recognized_text)
                response["keywords"] = keyword_result.get("keywords", [])
            except Exception as e:
                logger.warning(f"Keyword extraction failed: {e}")
        _pipeline_store[pipeline_id]["steps_completed"].append("keywords")

        # Step 6: Meeting Minutes
        if recognized_text and len(recognized_text) > 100:
            try:
                minutes_result = generate_minutes(recognized_text)
                response["meeting_minutes"] = minutes_result
            except Exception as e:
                logger.warning(f"Meeting minutes generation failed: {e}")
        _pipeline_store[pipeline_id]["steps_completed"].append("meeting_minutes")

        # Step 7: TTS generation
        audio_output_url = None
        if generate_tts and translated_text:
            try:
                tts_result = generate_speech(translated_text, language=target_lang or "en")
                audio_output_url = tts_result["audio_url"]
                response["audio_output_url"] = audio_output_url
            except Exception as e:
                logger.warning(f"TTS generation in pipeline failed: {e}")
        _pipeline_store[pipeline_id]["steps_completed"].append("tts")

        # Step 8: Save to history
        history = ProcessingHistory(
            user_id=user.id,
            audio_filename=upload_file.filename,
            audio_path=None,
            recognized_text=recognized_text,
            summary_text=summary_text,
            translated_text=translated_text,
            target_language=target_lang,
            source_language=detected_language,
            summary_mode=mode,
            audio_output_path=audio_output_url,
            sentiment=response.get("sentiment"),
            keywords=response.get("keywords"),
            meeting_minutes=response.get("meeting_minutes"),
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        response["history_id"] = history.id
        _pipeline_store[pipeline_id]["steps_completed"].append("save_history")

        # Step 9: Generate PDF report if requested
        if generate_report_flag and history.id:
            try:
                report_result = generate_report(db, user, history.id)
                response["report_url"] = report_result.get("report_url")
            except Exception as e:
                logger.warning(f"Report generation failed: {e}")

        _pipeline_store[pipeline_id]["status"] = "completed"
        _pipeline_store[pipeline_id]["result"] = response
        logger.info(f"Pipeline {pipeline_id} completed successfully")
        return response

    except Exception as e:
        _pipeline_store[pipeline_id]["status"] = "failed"
        _pipeline_store[pipeline_id]["error"] = str(e)
        logger.error(f"Pipeline {pipeline_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline processing failed: {str(e)}",
        )


def get_pipeline_status(pipeline_id: str) -> dict:
    pipeline = _pipeline_store.get(pipeline_id)
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )
    return {"pipeline_id": pipeline_id, **pipeline}

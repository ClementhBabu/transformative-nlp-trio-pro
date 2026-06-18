import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, UploadFile, status

from app.services.speech_service import speech_to_text

logger = logging.getLogger(__name__)

_minutes_store: dict = {}


def generate_minutes(text: str) -> dict:
    try:
        import nltk
        from nltk.tokenize import sent_tokenize

        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)

        sentences = sent_tokenize(text)

        # Extract title from first sentence
        title = sentences[0][:100] if sentences else "Untitled Meeting"

        # Simple heuristic extraction
        agenda_keywords = ["agenda", "topic", "discuss", "item"]
        action_keywords = ["need to", "will", "must", "should", "action", "assign"]
        decision_keywords = ["decided", "agreed", "approved", "concluded", "resolved"]
        next_keywords = ["next meeting", "follow up", "schedule", "next time"]

        agenda = []
        action_items = []
        decisions = []
        discussion_points = []

        for sent in sentences:
            lower = sent.lower()
            if any(kw in lower for kw in agenda_keywords):
                agenda.append(sent.strip())
                discussion_points.append(sent.strip())
            elif any(kw in lower for kw in action_keywords):
                action_items.append(sent.strip())
            elif any(kw in lower for kw in decision_keywords):
                decisions.append(sent.strip())
                discussion_points.append(sent.strip())
            elif any(kw in lower for kw in next_keywords):
                pass  # Handled below
            else:
                discussion_points.append(sent.strip()) if len(sent.strip()) > 20 else None

        next_meeting = None
        for sent in sentences:
            if any(kw in sent.lower() for kw in next_keywords):
                next_meeting = sent.strip()
                break

        return {
            "title": title,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "attendees": [],
            "agenda": agenda[:10] if agenda else discussion_points[:3],
            "discussion_points": discussion_points[:20],
            "action_items": action_items[:10],
            "decisions": decisions[:10] if decisions else ["Meeting held as planned"],
            "next_meeting": next_meeting,
        }
    except ImportError:
        logger.warning("NLTK not installed, returning placeholder minutes")
        return {
            "title": "Meeting Minutes",
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "attendees": [],
            "agenda": ["Discussion"],
            "discussion_points": text.split(". ")[:10],
            "action_items": ["Review and follow up"],
            "decisions": ["Meeting concluded"],
            "next_meeting": "TBD",
        }
    except Exception as e:
        logger.error(f"Meeting minutes generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meeting minutes generation failed: {str(e)}",
        )


async def generate_minutes_from_audio(
    upload_file: UploadFile,
    source_lang: Optional[str] = None,
) -> dict:
    stt_result = await speech_to_text(upload_file=upload_file, language=source_lang)
    recognized_text = stt_result["text"]
    minutes = generate_minutes(recognized_text)
    minutes_id = str(uuid.uuid4())
    _minutes_store[minutes_id] = minutes
    return {"minutes_id": minutes_id, "transcript": recognized_text, **minutes}


def get_minutes(minutes_id: str) -> dict:
    minutes = _minutes_store.get(minutes_id)
    if minutes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting minutes not found",
        )
    return minutes

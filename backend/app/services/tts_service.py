import logging
import os
import uuid
from typing import Optional

from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)

AVAILABLE_VOICES = [
    {"name": "female_en", "language": "en", "gender": "female", "description": "English Female"},
    {"name": "male_en", "language": "en", "gender": "male", "description": "English Male"},
    {"name": "female_es", "language": "es", "gender": "female", "description": "Spanish Female"},
    {"name": "female_fr", "language": "fr", "gender": "female", "description": "French Female"},
    {"name": "female_de", "language": "de", "gender": "female", "description": "German Female"},
    {"name": "female_it", "language": "it", "gender": "female", "description": "Italian Female"},
    {"name": "female_pt", "language": "pt", "gender": "female", "description": "Portuguese Female"},
    {"name": "female_zh", "language": "zh", "gender": "female", "description": "Chinese Female"},
    {"name": "female_ja", "language": "ja", "gender": "female", "description": "Japanese Female"},
    {"name": "male_ja", "language": "ja", "gender": "male", "description": "Japanese Male"},
    {"name": "female_ko", "language": "ko", "gender": "female", "description": "Korean Female"},
    {"name": "female_ar", "language": "ar", "gender": "female", "description": "Arabic Female"},
    {"name": "female_hi", "language": "hi", "gender": "female", "description": "Hindi Female"},
    {"name": "female_ru", "language": "ru", "gender": "female", "description": "Russian Female"},
]


def generate_speech(
    text: str,
    language: str = "en",
    gender: str = "female",
) -> dict:
    os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
    filename = f"tts_{uuid.uuid4().hex}_{language}_{gender}.mp3"
    file_path = os.path.join(settings.AUDIO_OUTPUT_DIR, filename)

    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(file_path)
    except ImportError:
        logger.warning("gTTS not installed, creating placeholder file")
        with open(file_path, "wb") as f:
            f.write(b"\x00" * 1024)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {language}",
        )
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS generation failed: {str(e)}",
        )

    logger.info(f"Generated TTS audio: {filename}")
    return {
        "audio_url": f"/api/tts/download/{filename}",
        "format": "mp3",
        "duration_seconds": None,
        "filename": filename,
    }


def get_voices(language: Optional[str] = None, gender: Optional[str] = None) -> dict:
    voices = AVAILABLE_VOICES
    if language:
        voices = [v for v in voices if v["language"] == language]
    if gender:
        voices = [v for v in voices if v["gender"] == gender]
    return {"voices": voices, "total": len(voices)}


def get_audio_path(filename: str) -> str:
    file_path = os.path.join(settings.AUDIO_OUTPUT_DIR, filename)
    safe_path = os.path.abspath(os.path.join(settings.AUDIO_OUTPUT_DIR, os.path.basename(filename)))
    if safe_path != file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found",
        )
    return file_path

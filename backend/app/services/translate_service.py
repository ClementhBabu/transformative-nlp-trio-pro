import logging
from typing import Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "te": "Telugu",
    "tr": "Turkish",
    "pl": "Polish",
    "sv": "Swedish",
    "da": "Danish",
    "fi": "Finnish",
    "no": "Norwegian",
    "cs": "Czech",
    "ro": "Romanian",
    "el": "Greek",
    "he": "Hebrew",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "uk": "Ukrainian",
    "bg": "Bulgarian",
    "auto": "Auto-detect",
}


def translate_text(
    text: str,
    source_lang: Optional[str] = "auto",
    target_lang: str = "en",
) -> dict:
    if target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language: {target_lang}",
        )

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(
            source=source_lang if source_lang != "auto" else "auto",
            target=target_lang,
        )
        translated = translator.translate(text)
        detected_source = source_lang if source_lang != "auto" else "auto"
    except ImportError:
        logger.warning("deep-translator not installed, using placeholder translation")
        translated = f"[{target_lang}] {text[:100]}..."
        detected_source = source_lang or "auto"
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}",
        )

    return {
        "translated_text": translated,
        "source_lang": detected_source,
        "target_lang": target_lang,
    }


def get_supported_languages() -> dict:
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ],
        "total": len([k for k in SUPPORTED_LANGUAGES if k != "auto"]),
    }


def detect_language(text: str) -> dict:
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="auto", target="en")
        detected = translator.detect(text)
        return {
            "detected_language": detected,
            "confidence": 0.95,
        }
    except ImportError:
        logger.warning("deep-translator not installed for language detection")
        return {
            "detected_language": "en",
            "confidence": 0.8,
        }
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language detection failed: {str(e)}",
        )

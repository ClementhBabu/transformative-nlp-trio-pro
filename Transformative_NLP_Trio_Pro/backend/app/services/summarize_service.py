import logging
from typing import Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

AVAILABLE_MODES = ["short", "medium", "detailed", "bullet"]


def summarize_text(text: str, mode: str = "medium") -> dict:
    if mode not in AVAILABLE_MODES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode '{mode}'. Available: {', '.join(AVAILABLE_MODES)}",
        )

    mode_config = {
        "short": {"max_length": 60, "min_length": 10},
        "medium": {"max_length": 150, "min_length": 30},
        "detailed": {"max_length": 300, "min_length": 80},
        "bullet": {"max_length": 200, "min_length": 40},
    }

    try:
        from transformers import pipeline
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
        )
        config = mode_config.get(mode, mode_config["medium"])
        result = summarizer(
            text,
            max_length=config["max_length"],
            min_length=config["min_length"],
            do_sample=False,
        )
        summary = result[0]["summary_text"]
    except ImportError:
        logger.warning("Transformers not installed, using placeholder summarization")
        words = text.split()
        if mode == "short":
            summary = " ".join(words[:20]) + "..."
        elif mode == "bullet":
            summary = "• " + "\n• ".join(text.split(". ")[:3])
        elif mode == "detailed":
            summary = "Detailed summary: " + text[:300]
        else:
            summary = " ".join(words[:50]) + "..."
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}",
        )

    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "mode": mode,
    }


def summarize_batch(texts: list[str], mode: str = "medium") -> dict:
    results = []
    for text in texts:
        try:
            results.append(summarize_text(text, mode))
        except Exception as e:
            results.append({
                "summary": None,
                "original_length": len(text),
                "summary_length": 0,
                "mode": mode,
                "error": str(e),
            })
    return {"results": results, "total": len(results)}


def get_available_modes() -> dict:
    return {
        "modes": [
            {"name": "short", "description": "Brief 1-2 sentence summary"},
            {"name": "medium", "description": "Moderate length paragraph summary"},
            {"name": "detailed", "description": "Comprehensive detailed summary"},
            {"name": "bullet", "description": "Bullet-point key takeaways"},
        ],
        "default": "medium",
    }

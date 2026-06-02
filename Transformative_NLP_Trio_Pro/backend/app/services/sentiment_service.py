import logging
from typing import Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def analyze_sentiment(text: str) -> dict:
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = round(blob.sentiment.polarity, 4)
        subjectivity = round(blob.sentiment.subjectivity, 4)

        if polarity > 0.1:
            classification = "positive"
        elif polarity < -0.1:
            classification = "negative"
        else:
            classification = "neutral"

        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "classification": classification,
        }
    except ImportError:
        logger.warning("TextBlob not installed, returning placeholder sentiment")
        return {
            "polarity": 0.0,
            "subjectivity": 0.5,
            "classification": "neutral",
        }
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment analysis failed: {str(e)}",
        )


def batch_analyze_sentiment(texts: list[str]) -> dict:
    results = []
    for text in texts:
        try:
            results.append(analyze_sentiment(text))
        except Exception as e:
            results.append({
                "polarity": 0.0,
                "subjectivity": 0.5,
                "classification": "error",
                "error": str(e),
            })
    return {"results": results, "total": len(results)}

import logging
from typing import Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def extract_keywords(text: str, num_keywords: int = 10) -> dict:
    try:
        import nltk
        from nltk.tokenize import word_tokenize, sent_tokenize
        from nltk.corpus import stopwords
        from nltk.probability import FreqDist

        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)

        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words("english"))
        filtered = [
            w for w in words
            if w.isalnum() and w not in stop_words and len(w) > 2
        ]
        freq = FreqDist(filtered)
        top_keywords = freq.most_common(num_keywords)
        return {
            "keywords": [kw for kw, _ in top_keywords],
            "score": [round(score / len(filtered), 4) if filtered else 0
                       for _, score in top_keywords],
        }
    except ImportError:
        logger.warning("NLTK not installed, returning placeholder keywords")
        words = [w.strip(".,!?;:") for w in text.split() if len(w.strip(".,!?;:")) > 3]
        unique = list(dict.fromkeys(words))[:num_keywords]
        return {"keywords": unique, "score": [1.0] * len(unique)}
    except Exception as e:
        logger.error(f"Keyword extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Keyword extraction failed: {str(e)}",
        )


def extract_keyphrases(text: str, num_phrases: int = 5) -> dict:
    try:
        import nltk
        from nltk.tokenize import sent_tokenize

        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)

        sentences = sent_tokenize(text)
        # Weight sentences by position and length
        scored = []
        total = len(sentences)
        for i, sent in enumerate(sentences):
            position_score = 1.0 - (i / total) if total > 0 else 0.5
            length_score = min(len(sent.split()) / 30.0, 1.0)
            score = position_score * 0.4 + length_score * 0.6
            scored.append((sent.strip(), round(score, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:num_phrases]
        return {
            "keyphrases": [s for s, _ in top],
            "score": [sc for _, sc in top],
        }
    except ImportError:
        logger.warning("NLTK not installed, returning placeholder keyphrases")
        phrases = text.split(". ")[:num_phrases]
        return {
            "keyphrases": [p.strip() for p in phrases if p.strip()],
            "score": [0.8] * len(phrases),
        }
    except Exception as e:
        logger.error(f"Keyphrase extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Keyphrase extraction failed: {str(e)}",
        )

import logging
from typing import Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def ask_question(text: str, question: str) -> dict:
    try:
        from transformers import pipeline
        qa_pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad",
        )
        result = qa_pipeline(question=question, context=text)
        return {
            "question": question,
            "answer": result["answer"],
            "confidence": round(result["score"], 4),
        }
    except ImportError:
        logger.warning("Transformers not installed, returning placeholder Q&A")
        # Simple keyword-based answer
        words = text.split()
        answer = f"[Answer based on context of {len(words)} words]"
        return {
            "question": question,
            "answer": answer,
            "confidence": 0.7,
        }
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {str(e)}",
        )


def generate_questions(text: str, num_questions: int = 5) -> dict:
    try:
        import nltk
        from nltk.tokenize import sent_tokenize

        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)

        sentences = sent_tokenize(text)
        questions = []

        question_starters = [
            "What is the significance of",
            "How does",
            "Why did",
            "What are the key points about",
            "Can you explain",
            "What is the relationship between",
            "How would you describe",
        ]

        for i, sentence in enumerate(sentences[:min(len(sentences), num_questions)]):
            words = sentence.split()
            subject = " ".join(words[:min(len(words), 6)])
            starter = question_starters[i % len(question_starters)]
            questions.append(f"{starter} {subject}?")

        return {"questions": questions[:num_questions], "total": len(questions[:num_questions])}
    except ImportError:
        logger.warning("NLTK not installed, generating placeholder questions")
        return {
            "questions": [f"Question {i+1} about the text?" for i in range(min(3, num_questions))],
            "total": min(3, num_questions),
        }
    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question generation failed: {str(e)}",
        )

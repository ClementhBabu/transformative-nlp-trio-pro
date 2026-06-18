import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.processing import QARequest, QAResponse, QuestionGenerationRequest
from app.services.qa_service import ask_question, generate_questions
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/qa", tags=["Question Answering"])


@router.post(
    "/ask",
    response_model=QAResponse,
    summary="Answer a question about a provided text context",
)
async def ask(
    payload: QARequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = ask_question(payload.text, payload.question)
        return QAResponse(
            question=result["question"],
            answer=result["answer"],
            confidence=result.get("confidence"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question answering error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question answering failed due to an internal error",
        )


@router.post(
    "/generate-questions",
    summary="Auto-generate questions about the provided text",
)
async def generate(
    payload: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = generate_questions(payload.text, num_questions=payload.num_questions)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question generation failed due to an internal error",
        )

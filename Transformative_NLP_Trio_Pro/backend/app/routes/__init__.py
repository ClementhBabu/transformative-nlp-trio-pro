from fastapi import APIRouter, HTTPException

from app.routes.auth import router as auth_router
from app.routes.speech import router as speech_router
from app.routes.summarize import router as summarize_router
from app.routes.translate import router as translate_router
from app.routes.tts import router as tts_router
from app.routes.pipeline import router as pipeline_router
from app.routes.history import router as history_router
from app.routes.analytics import router as analytics_router
from app.routes.report import router as report_router
from app.routes.sentiment import router as sentiment_router
from app.routes.keywords import router as keywords_router
from app.routes.qa import router as qa_router
from app.routes.meeting import router as meeting_router
from app.routes.websocket import router as websocket_router

__all__ = [
    "auth_router",
    "speech_router",
    "summarize_router",
    "translate_router",
    "tts_router",
    "pipeline_router",
    "history_router",
    "analytics_router",
    "report_router",
    "sentiment_router",
    "keywords_router",
    "qa_router",
    "meeting_router",
    "websocket_router",
]

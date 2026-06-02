from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.database import init_db
from app.routes import (
    auth_router,
    speech_router,
    summarize_router,
    translate_router,
    tts_router,
    pipeline_router,
    history_router,
    analytics_router,
    report_router,
    sentiment_router,
    keywords_router,
    qa_router,
    meeting_router,
    websocket_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(speech_router)
app.include_router(summarize_router)
app.include_router(translate_router)
app.include_router(tts_router)
app.include_router(pipeline_router)
app.include_router(history_router)
app.include_router(analytics_router)
app.include_router(report_router)
app.include_router(sentiment_router)
app.include_router(keywords_router)
app.include_router(qa_router)
app.include_router(meeting_router)
app.include_router(websocket_router)


@app.get("/")
async def root() -> dict:
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
    }


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )

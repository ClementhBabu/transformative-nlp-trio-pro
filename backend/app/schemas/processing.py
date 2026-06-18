from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AudioUploadResponse(BaseModel):
    filename: str
    file_path: str
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None


class SpeechToTextRequest(BaseModel):
    language: Optional[str] = Field(None, description="Source language code (e.g., en, es, fr)")


class SpeechToTextResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: str = Field("medium", description="short, medium, detailed, bullet")


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    mode: str


class BatchSummarizeRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)
    mode: str = Field("medium", description="short, medium, detailed, bullet")


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source_lang: Optional[str] = Field("auto", description="Source language code")
    target_lang: str = Field(..., min_length=2, max_length=10)


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str


class LanguageDetectRequest(BaseModel):
    text: str = Field(..., min_length=1)


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = Field("en", description="Language code for TTS voice")
    gender: Optional[str] = Field("female", description="male or female")


class TTSResponse(BaseModel):
    audio_url: str
    format: str = "mp3"
    duration_seconds: Optional[float] = None


class ProcessingPipelineRequest(BaseModel):
    mode: str = Field("medium", description="Summarization mode")
    target_lang: Optional[str] = Field(None, description="Target language for translation")
    source_lang: Optional[str] = Field(None, description="Source language for STT")
    generate_tts: bool = Field(True, description="Whether to generate TTS output")
    generate_report: bool = Field(False, description="Whether to generate PDF report")


class ProcessingPipelineResponse(BaseModel):
    history_id: UUID
    recognized_text: Optional[str] = None
    summary_text: Optional[str] = None
    translated_text: Optional[str] = None
    sentiment: Optional[dict] = None
    keywords: Optional[list] = None
    meeting_minutes: Optional[dict] = None
    audio_output_url: Optional[str] = None
    report_url: Optional[str] = None


class HistoryResponse(BaseModel):
    id: UUID
    audio_filename: Optional[str] = None
    recognized_text: Optional[str] = None
    summary_text: Optional[str] = None
    translated_text: Optional[str] = None
    target_language: Optional[str] = None
    source_language: Optional[str] = None
    summary_mode: Optional[str] = None
    audio_output_path: Optional[str] = None
    sentiment: Optional[Any] = None
    keywords: Optional[Any] = None
    meeting_minutes: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    id: UUID
    operation_type: str
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    duration_ms: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1)


class BatchSentimentRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)


class SentimentResponse(BaseModel):
    polarity: float
    subjectivity: float
    classification: str


class KeywordRequest(BaseModel):
    text: str = Field(..., min_length=1)
    num_keywords: int = Field(10, ge=1, le=50, description="Number of keywords to extract")


class KeyphraseRequest(BaseModel):
    text: str = Field(..., min_length=1)


class KeywordResponse(BaseModel):
    keywords: list[str]
    score: Optional[list[float]] = None


class QARequest(BaseModel):
    text: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


class QuestionGenerationRequest(BaseModel):
    text: str = Field(..., min_length=1)
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions to generate")


class QAResponse(BaseModel):
    question: str
    answer: str
    confidence: Optional[float] = None


class MeetingMinutesRequest(BaseModel):
    text: str = Field(..., min_length=1)


class MeetingMinutesResponse(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    attendees: Optional[list[str]] = None
    agenda: Optional[list[str]] = None
    discussion_points: Optional[list[str]] = None
    action_items: Optional[list[str]] = None
    decisions: Optional[list[str]] = None
    next_meeting: Optional[str] = None


class ReportRequest(BaseModel):
    history_id: UUID


class ReportResponse(BaseModel):
    filename: str
    report_url: str
    generated_at: datetime

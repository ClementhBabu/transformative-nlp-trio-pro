import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Transformative NLP Trio Pro"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Voice Recognition, Summarization, Translation & TTS System"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nlp_trio"
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    UPLOAD_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "uploads"
    )
    AUDIO_OUTPUT_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "generated_audio"
    )
    REPORTS_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "reports"
    )

    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    SUMMARIZATION_MODEL: str = os.getenv(
        "SUMMARIZATION_MODEL", "facebook/bart-large-cnn"
    )
    TTS_ENGINE: str = os.getenv("TTS_ENGINE", "gtts")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_AUDIO_EXTENSIONS: list = ["wav", "mp3", "m4a", "ogg", "webm"]

    class Config:
        env_file = ".env"


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)

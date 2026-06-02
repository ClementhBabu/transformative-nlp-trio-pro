import os
import uuid
import shutil
import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = set(settings.ALLOWED_AUDIO_EXTENSIONS)
MAX_UPLOAD_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def validate_audio_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


async def save_upload_file(
    upload_file: UploadFile,
    directory: str,
    allowed_extensions: set = None,
    max_size: int = None,
) -> str:
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    if max_size is None:
        max_size = MAX_UPLOAD_SIZE_BYTES

    filename = upload_file.filename or "unknown"
    
    # If the filename has no extension (e.g. "blob" or "unknown"), guess it from content_type
    if "." not in filename:
        content_type = upload_file.content_type or ""
        guessed_ext = None
        if "webm" in content_type:
            guessed_ext = "webm"
        elif "wav" in content_type:
            guessed_ext = "wav"
        elif "mpeg" in content_type or "mp3" in content_type:
            guessed_ext = "mp3"
        elif "ogg" in content_type:
            guessed_ext = "ogg"
        elif "mp4" in content_type or "m4a" in content_type:
            guessed_ext = "m4a"
            
        if guessed_ext:
            filename = f"{filename}.{guessed_ext}"
            upload_file.filename = filename

    if not validate_audio_file(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(sorted(allowed_extensions))}",
        )

    file_ext = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(directory, unique_name)

    os.makedirs(directory, exist_ok=True)

    file_size = 0
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await upload_file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > max_size:
                    cleanup_file(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB",
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        cleanup_file(file_path)
        logger.error(f"Failed to save upload file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file",
        )

    logger.info(f"Saved upload file: {file_path} ({file_size} bytes)")
    return file_path


def cleanup_file(file_path: str) -> None:
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {e}")


def get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def ensure_directory(dir_path: str) -> None:
    os.makedirs(dir_path, exist_ok=True)

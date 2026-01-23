import os
import secrets
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from typing import Optional


MEDIA_DIR = Path("media")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def ensure_media_dir():
    MEDIA_DIR.mkdir(exist_ok=True)


async def save_uploaded_file(
    file: UploadFile,
    subdirectory: str = "",
    max_size: int = MAX_FILE_SIZE
) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, GIF, or WebP)"
        )
    
    contents = await file.read()
    
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {max_size // (1024 * 1024)}MB"
        )
    
    file_extension = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if file_extension not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        file_extension = ".jpg"
    
    safe_filename = f"{secrets.token_urlsafe(16)}{file_extension}"
    
    if subdirectory:
        target_dir = MEDIA_DIR / subdirectory
        target_dir.mkdir(exist_ok=True)
        file_path = target_dir / safe_filename
        relative_path = f"{subdirectory}/{safe_filename}"
    else:
        file_path = MEDIA_DIR / safe_filename
        relative_path = safe_filename
    
    ensure_media_dir()
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return relative_path


async def delete_file(file_path: str) -> None:
    if not file_path:
        return
    
    full_path = MEDIA_DIR / file_path
    if full_path.exists():
        try:
            full_path.unlink()
        except Exception:
            pass

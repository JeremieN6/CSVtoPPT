"""Utility helpers for the backend API layer."""
from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile

# Upload caps to protect the server
MAX_UPLOAD_SIZE_CSV = 15 * 1024 * 1024  # 15 MB for CSV-like files
MAX_UPLOAD_SIZE_EXCEL = 8 * 1024 * 1024  # 8 MB for Excel
ALLOWED_EXTENSIONS = {".csv", ".tsv", ".txt", ".xlsx", ".xls"}


def slugify(text: str, fallback: str = "rapport") -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", text or "").strip("-").lower()
    return normalized or fallback


def is_allowed_extension(filename: str) -> bool:
    suffix = Path(filename or "").suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def make_temp_dir(prefix: str = "csvtoppt_") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


def cleanup_path(path: Optional[Path]) -> None:
    if not path:
        return
    shutil.rmtree(path, ignore_errors=True)


def safe_delete_file(path: str | Path) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_generated_filename(title: str) -> str:
    return f"{slugify(title)}_{uuid4().hex[:8]}.pptx"


async def save_upload_file(upload: UploadFile, destination_dir: Path) -> Path:
    ensure_directory(destination_dir)
    suffix = Path(upload.filename or "").suffix or ".csv"
    temp_path = destination_dir / f"{uuid4().hex}{suffix}"
    
    with temp_path.open("wb") as buffer:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            buffer.write(chunk)
    
    await upload.seek(0)
    return temp_path


def validate_file_size(path: Path) -> None:
    size = path.stat().st_size
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        limit = MAX_UPLOAD_SIZE_EXCEL
        label = "8 Mo pour les fichiers Excel"
    else:
        limit = MAX_UPLOAD_SIZE_CSV
        label = "15 Mo pour les fichiers CSV/TSV/TXT"

    if size > limit:
        raise ValueError(f"Fichier trop volumineux (maximum {label}).")

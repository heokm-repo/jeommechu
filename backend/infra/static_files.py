from __future__ import annotations

from pathlib import Path


CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".webmanifest": "application/json; charset=utf-8",
    ".png": "image/png",
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".svg": "image/svg+xml",
}


def resolve_static_file(root_dir: Path, request_path: str) -> Path | None:
    root_dir = root_dir.resolve()
    rel_path = request_path.lstrip("/")
    file_path = root_dir / "index.html" if rel_path in ("", "index.html") else root_dir / rel_path
    file_path = file_path.resolve()

    try:
        file_path.relative_to(root_dir)
    except ValueError:
        return None

    return file_path


def content_type_for(file_path: Path) -> str:
    return CONTENT_TYPES.get(file_path.suffix.lower(), "application/octet-stream")

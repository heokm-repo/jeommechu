from __future__ import annotations

from http.server import BaseHTTPRequestHandler
from pathlib import Path

try:
    from .static_files import content_type_for, resolve_static_file
except ImportError:
    from infra.static_files import content_type_for, resolve_static_file


def serve_static_file(handler: BaseHTTPRequestHandler, root_dir: Path, request_path: str) -> None:
    file_path = resolve_static_file(root_dir, request_path)
    if file_path is None:
        handler.send_error(403, "Access denied")
        return
    if not file_path.exists() or not file_path.is_file():
        handler.send_error(404, "File not found")
        return

    try:
        data = file_path.read_bytes()
    except OSError as exc:
        handler.send_error(500, f"Internal server error: {str(exc)}")
        return

    handler.send_response(200)
    handler.send_header("Content-Type", content_type_for(file_path))
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)
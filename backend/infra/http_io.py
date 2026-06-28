from __future__ import annotations

import json
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from typing import Any

try:
    from .database import IntegrityError
    from ..utils import HttpError
except ImportError:
    from infra.database import IntegrityError
    from utils import HttpError

ApiResponse = tuple[int, dict[str, Any]] | tuple[int, dict[str, Any], dict[str, str]]


def read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    content_length = int(handler.headers.get("Content-Length") or 0)
    if content_length == 0:
        return {}
    raw_body = handler.rfile.read(content_length).decode("utf-8")
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON body") from exc
    if not isinstance(payload, dict):
        raise ValueError("JSON body must be an object")
    return payload


def read_cookies(handler: BaseHTTPRequestHandler) -> dict[str, str]:
    raw_cookie = handler.headers.get("Cookie") or ""
    if not raw_cookie:
        return {}
    cookie = SimpleCookie()
    cookie.load(raw_cookie)
    return {key: morsel.value for key, morsel in cookie.items()}


def write_json(
    handler: BaseHTTPRequestHandler,
    status: int,
    body: dict[str, Any],
    headers: dict[str, str] | None = None,
) -> None:
    response = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(response)))
    for key, value in (headers or {}).items():
        handler.send_header(key, value)
    handler.end_headers()
    handler.wfile.write(response)


def write_api_response(handler: BaseHTTPRequestHandler, response: ApiResponse | None, fallback: ApiResponse) -> None:
    headers: dict[str, str] = {}
    if response is None:
        status, body = fallback
    elif len(response) == 3:
        status, body, headers = response
    else:
        status, body = response
    write_json(handler, status, body, headers)


def write_error_response(handler: BaseHTTPRequestHandler, exc: Exception) -> None:
    if isinstance(exc, HttpError):
        write_json(handler, exc.status_code, {"error": str(exc)})
        return
    if isinstance(exc, ValueError):
        write_json(handler, 400, {"error": str(exc)})
        return
    if isinstance(exc, IntegrityError):
        write_json(handler, 409, {"error": "Database constraint failed", "detail": str(exc)})
        return
    write_json(handler, 500, {"error": "Internal server error", "detail": str(exc)})
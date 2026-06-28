from __future__ import annotations

from typing import Any

from .common import ApiResponse

try:
    from ..services.auth_service import SESSION_COOKIE_NAME, auth_login, auth_logout, auth_signup
except ImportError:
    from services.auth_service import SESSION_COOKIE_NAME, auth_login, auth_logout, auth_signup


def auth_response(status: int, result: tuple[dict[str, Any], str]) -> ApiResponse:
    body, cookie = result
    return status, body, {"Set-Cookie": cookie}


def post_auth_signup(payload: dict[str, Any], cookies: dict[str, str]) -> ApiResponse:
    return auth_response(201, auth_signup(payload, cookies.get(SESSION_COOKIE_NAME)))


def post_auth_login(payload: dict[str, Any], _cookies: dict[str, str]) -> ApiResponse:
    return auth_response(200, auth_login(payload))


def post_auth_logout(payload: dict[str, Any], cookies: dict[str, str]) -> ApiResponse:
    return auth_response(200, auth_logout(payload, cookies.get(SESSION_COOKIE_NAME)))
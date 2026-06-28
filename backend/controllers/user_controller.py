from __future__ import annotations

from typing import Any

from .common import ApiResponse

try:
    from ..services.auth_service import SESSION_COOKIE_NAME, current_session_user_id
    from ..services.user_service import create_guest_user, create_guest_user_with_session
except ImportError:
    from services.auth_service import SESSION_COOKIE_NAME, current_session_user_id
    from services.user_service import create_guest_user, create_guest_user_with_session


def post_guest_user(_payload: dict[str, Any], cookies: dict[str, str]) -> ApiResponse:
    user_id = current_session_user_id(cookies.get(SESSION_COOKIE_NAME))
    if user_id:
        return 200, {"user_id": user_id}

    body, cookie = create_guest_user_with_session()
    return 201, body, {"Set-Cookie": cookie}
from __future__ import annotations

from typing import Any

from .common import ApiResponse, not_found

try:
    from ..services.activity_service import create_feedback, get_search, get_search_owner_user_id
    from ..services.auth_service import (
        SESSION_COOKIE_NAME,
        create_session_cookie_for_user,
        current_session_user_id,
        require_session_owner,
        require_session_user_id,
    )
    from ..services.recommendation_service import create_recommendation_search
    from ..utils import AuthorizationError
except ImportError:
    from services.activity_service import create_feedback, get_search, get_search_owner_user_id
    from services.auth_service import (
        SESSION_COOKIE_NAME,
        create_session_cookie_for_user,
        current_session_user_id,
        require_session_owner,
        require_session_user_id,
    )
    from services.recommendation_service import create_recommendation_search
    from utils import AuthorizationError


def session_token(cookies: dict[str, str]) -> str | None:
    return cookies.get(SESSION_COOKIE_NAME)


def handle_recommendation_detail(path: str, cookies: dict[str, str]) -> ApiResponse | None:
    if not path.startswith("/api/recommendations/"):
        return None

    parts = path.strip("/").split("/")
    if len(parts) != 3:
        return not_found()

    session_user_id = require_session_user_id(session_token(cookies))
    search_log_id = parts[2]
    result = get_search(search_log_id)
    if result is None:
        return 404, {"error": "Search log not found"}
    if result["search"].get("user_id") != session_user_id:
        raise AuthorizationError("You can only access your own recommendation history")
    return 200, result


def handle_recommendation_feedback(path: str, payload: dict[str, Any], cookies: dict[str, str]) -> ApiResponse | None:
    if not (path.startswith("/api/recommendations/") and path.endswith("/feedback")):
        return None

    parts = path.strip("/").split("/")
    if len(parts) != 4:
        return not_found()

    session_user_id = require_session_user_id(session_token(cookies))
    search_log_id = parts[2]
    owner_user_id = get_search_owner_user_id(search_log_id)
    if owner_user_id is None:
        return 404, {"error": "Search log not found"}
    if owner_user_id != session_user_id:
        raise AuthorizationError("You can only add feedback to your own recommendation history")

    return 201, create_feedback(search_log_id, {**payload, "user_id": session_user_id})


def post_recommendation_search(payload: dict[str, Any], cookies: dict[str, str]) -> ApiResponse:
    request_payload = dict(payload)
    requested_user_id = request_payload.get("user_id")
    existing_session_user_id = current_session_user_id(session_token(cookies))
    should_issue_session = False

    if isinstance(requested_user_id, str) and requested_user_id.strip():
        request_payload["user_id"] = require_session_owner(session_token(cookies), requested_user_id)
    elif existing_session_user_id:
        request_payload["user_id"] = existing_session_user_id
    else:
        request_payload.pop("user_id", None)
        should_issue_session = True

    body = create_recommendation_search(request_payload)
    if not should_issue_session:
        return 201, body

    session_body, cookie = create_session_cookie_for_user(body["user_id"])
    return 201, {**body, **session_body}, {"Set-Cookie": cookie}
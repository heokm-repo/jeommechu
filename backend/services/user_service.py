from __future__ import annotations

try:
    from ..infra.database import connect
    from ..repositories.recommendation_repository import ensure_guest_user
    from .auth_service import create_session, session_cookie
    from ..utils import utc_now
except ImportError:
    from infra.database import connect
    from repositories.recommendation_repository import ensure_guest_user
    from services.auth_service import create_session, session_cookie
    from utils import utc_now


def create_guest_user() -> dict[str, str]:
    with connect() as conn:
        with conn:
            user_id = ensure_guest_user(conn)
    return {"user_id": user_id}


def create_guest_user_with_session() -> tuple[dict[str, object], str]:
    now = utc_now()
    with connect() as conn:
        with conn:
            user_id = ensure_guest_user(conn)
            session_token, expires_at = create_session(conn, user_id, now)
    return {"user_id": user_id, "session": {"expires_at": expires_at}}, session_cookie(session_token)
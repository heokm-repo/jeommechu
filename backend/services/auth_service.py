from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from ..infra.database import connect
    from ..utils import AuthenticationError, AuthorizationError, new_id, require_text, utc_now
except ImportError:
    from infra.database import connect
    from utils import AuthenticationError, AuthorizationError, new_id, require_text, utc_now

SESSION_COOKIE_NAME = "jeommechu_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str, salt: str | None = None) -> str:
    if len(password) < 6:
        raise ValueError("비밀번호는 6자 이상이어야 합니다.")
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    try:
        algorithm, salt, expected = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return hmac.compare_digest(digest, expected)


def user_public(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "user_type": row["user_type"],
        "auth_provider": row["auth_provider"],
        "email": row["email"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def utc_timestamp_after(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S.%f")


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_cookie(token: str, max_age: int = SESSION_MAX_AGE_SECONDS) -> str:
    return f"{SESSION_COOKIE_NAME}={token}; Path=/; Max-Age={max_age}; HttpOnly; SameSite=Lax"


def clear_session_cookie() -> str:
    return session_cookie("", 0)


def current_session_user_id(session_token: str | None) -> str | None:
    if not session_token:
        return None
    with connect() as conn:
        row = conn.execute(
            """
            SELECT s.user_id
            FROM auth_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.session_token_hash = ?
              AND s.revoked_at IS NULL
              AND s.expires_at > ?
              AND u.status = 'ACTIVE'
            LIMIT 1
            """,
            (hash_session_token(session_token), utc_now()),
        ).fetchone()
    return row["user_id"] if row else None


def require_session_user_id(session_token: str | None) -> str:
    user_id = current_session_user_id(session_token)
    if not user_id:
        raise AuthenticationError()
    return user_id


def normalize_requested_user_id(requested_user_id: Any) -> str:
    if not isinstance(requested_user_id, str) or not requested_user_id.strip():
        raise ValueError("'user_id' is required")
    return requested_user_id.strip()


def require_session_owner(session_token: str | None, requested_user_id: Any) -> str:
    user_id = normalize_requested_user_id(requested_user_id)
    session_user_id = require_session_user_id(session_token)
    if session_user_id != user_id:
        raise AuthorizationError("You can only access your own user data")
    return user_id


def create_session_cookie_for_user(user_id: str) -> tuple[dict[str, Any], str]:
    now = utc_now()
    with connect() as conn:
        with conn:
            user = conn.execute("SELECT id FROM users WHERE id = ? AND status = 'ACTIVE'", (user_id,)).fetchone()
            if not user:
                raise AuthenticationError()
            session_token, expires_at = create_session(conn, user_id, now)
    return {"session": {"expires_at": expires_at}}, session_cookie(session_token)


def create_session(conn: Any, user_id: str, now: str) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    expires_at = utc_timestamp_after(SESSION_MAX_AGE_SECONDS)
    conn.execute(
        """
        INSERT INTO auth_sessions (
          id, user_id, session_token_hash, expires_at, revoked_at, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, NULL, ?, ?)
        """,
        (new_id(), user_id, hash_session_token(token), expires_at, now, now),
    )
    return token, expires_at


def revoke_session(conn: Any, session_token: str | None, now: str) -> int:
    if not session_token:
        return 0
    result = conn.execute(
        """
        UPDATE auth_sessions
        SET revoked_at = ?, updated_at = ?
        WHERE session_token_hash = ? AND revoked_at IS NULL
        """,
        (now, now, hash_session_token(session_token)),
    )
    return result.rowcount


def auth_signup(payload: dict[str, Any], session_token: str | None = None) -> tuple[dict[str, Any], str]:
    email = normalize_email(require_text(payload, "email"))
    password = require_text(payload, "password")
    now = utc_now()
    password_hash = hash_password(password)

    with connect() as conn:
        with conn:
            existing = conn.execute(
                "SELECT * FROM users WHERE auth_provider = 'EMAIL' AND provider_user_id = ? AND status = 'ACTIVE'",
                (email,),
            ).fetchone()
            if existing:
                raise ValueError("이미 가입된 이메일입니다.")

            user_id = payload.get("user_id")
            user = None
            if user_id:
                user_id = require_session_owner(session_token, user_id)
                user = conn.execute("SELECT * FROM users WHERE id = ? AND status = 'ACTIVE'", (user_id,)).fetchone()

            if user:
                conn.execute(
                    """
                    UPDATE users
                    SET user_type = 'MEMBER', auth_provider = 'EMAIL', provider_user_id = ?,
                        email = ?, password_hash = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (email, email, password_hash, now, user_id),
                )
            else:
                user_id = new_id()
                conn.execute(
                    """
                    INSERT INTO users (
                      id, user_type, auth_provider, provider_user_id, email,
                      password_hash, status, created_at, updated_at
                    )
                    VALUES (?, 'MEMBER', 'EMAIL', ?, ?, ?, 'ACTIVE', ?, ?)
                    """,
                    (user_id, email, email, password_hash, now, now),
                )

            created = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            session_token, expires_at = create_session(conn, user_id, now)

    return {"user": user_public(created), "session": {"expires_at": expires_at}}, session_cookie(session_token)


def auth_login(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    email = normalize_email(require_text(payload, "email"))
    password = require_text(payload, "password")
    now = utc_now()
    with connect() as conn:
        with conn:
            user = conn.execute(
                "SELECT * FROM users WHERE auth_provider = 'EMAIL' AND provider_user_id = ? AND status = 'ACTIVE'",
                (email,),
            ).fetchone()
            if not user or not verify_password(password, user["password_hash"]):
                raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
            session_token, expires_at = create_session(conn, user["id"], now)
    return {"user": user_public(user), "session": {"expires_at": expires_at}}, session_cookie(session_token)


def auth_logout(payload: dict[str, Any], session_token: str | None = None) -> tuple[dict[str, Any], str]:
    now = utc_now()
    revoked = 0
    if session_token:
        with connect() as conn:
            with conn:
                revoked = revoke_session(conn, session_token, now)
    return {"ok": True, "session_revoked": revoked > 0}, clear_session_cookie()
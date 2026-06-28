from __future__ import annotations

from typing import Any

try:
    from ..infra.database import MySQLConnection
    from ..utils import new_id, to_json, utc_now
except ImportError:
    from infra.database import MySQLConnection
    from utils import new_id, to_json, utc_now


def ensure_guest_user(conn: MySQLConnection, user_id: str | None = None) -> str:
    if user_id:
        existing = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if existing:
            return user_id

    now = utc_now()
    created_user_id = new_id()
    conn.execute(
        """
        INSERT INTO users (id, user_type, auth_provider, status, created_at, updated_at)
        VALUES (?, 'GUEST', 'NONE', 'ACTIVE', ?, ?)
        """,
        (created_user_id, now, now),
    )
    return created_user_id


def insert_search_log(
    conn: MySQLConnection,
    *,
    user_id: str,
    latitude: Any,
    longitude: Any,
    address_text: Any,
    emotion_state: str,
    search_context: Any,
    now: str,
) -> str:
    search_log_id = new_id()
    conn.execute(
        """
        INSERT INTO search_logs (
          id, user_id, latitude, longitude, address_text,
          emotion_state, search_context, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (search_log_id, user_id, latitude, longitude, address_text, emotion_state, search_context, now, now),
    )
    return search_log_id


def insert_ai_response(
    conn: MySQLConnection,
    *,
    search_log_id: str,
    model_name: str,
    prompt_text: str,
    response_text: Any,
    now: str,
) -> None:
    conn.execute(
        """
        INSERT INTO ai_responses (
          id, search_log_id, model_name, prompt_text, response_text, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (new_id(), search_log_id, model_name, prompt_text, to_json(response_text), now, now),
    )


def insert_keywords(conn: MySQLConnection, search_log_id: str, keywords: list[Any], now: str) -> None:
    for item in keywords:
        if not isinstance(item, dict):
            continue
        keyword = item.get("keyword")
        keyword_type = item.get("keyword_type")
        if not keyword or not keyword_type:
            continue
        conn.execute(
            """
            INSERT INTO ai_extracted_keywords (
              id, search_log_id, keyword, keyword_type, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (new_id(), search_log_id, keyword, keyword_type, now, now),
        )


def insert_search_recommendation(
    conn: MySQLConnection,
    *,
    search_log_id: str,
    restaurant_id: str,
    rank: int,
    score: Any,
    ai_reason: Any,
    now: str,
) -> str:
    recommendation_id = new_id()
    conn.execute(
        """
        INSERT INTO search_recommendations (
          id, search_log_id, restaurant_id, recommendation_rank,
          score, ai_reason, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (recommendation_id, search_log_id, restaurant_id, rank, score, ai_reason, now, now),
    )
    return recommendation_id


def insert_recommendation_log(
    conn: MySQLConnection,
    *,
    search_log_id: str,
    payload: dict[str, Any],
    now: str,
) -> None:
    conn.execute(
        """
        INSERT INTO recommendation_logs (id, search_log_id, log_type, payload, created_at, updated_at)
        VALUES (?, ?, 'SEARCH', ?, ?, ?)
        """,
        (new_id(), search_log_id, to_json(payload), now, now),
    )


def save_search_recommendations(
    conn: MySQLConnection,
    *,
    search_log_id: str,
    restaurants: list[dict[str, Any]],
    ai_reason: str,
    now: str,
) -> list[dict[str, Any]]:
    saved_recommendations = []
    for rank, restaurant in enumerate(restaurants, start=1):
        score = 100 - rank
        recommendation_id = insert_search_recommendation(
            conn,
            search_log_id=search_log_id,
            restaurant_id=restaurant["id"],
            rank=rank,
            score=score,
            ai_reason=ai_reason,
            now=now,
        )
        saved_recommendations.append(
            {
                "id": recommendation_id,
                "restaurant_id": restaurant["id"],
                "rank": rank,
                "score": score,
                "ai_reason": ai_reason,
                "restaurant": restaurant,
            }
        )
    return saved_recommendations
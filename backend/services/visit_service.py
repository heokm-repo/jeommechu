from __future__ import annotations

from typing import Any

try:
    from ..repositories.activity_repository import insert_recommendation_log
    from ..infra.database import connect
    from ..utils import clamp_int, new_id, require_text, row_to_dict, utc_now
except ImportError:
    from repositories.activity_repository import insert_recommendation_log
    from infra.database import connect
    from utils import clamp_int, new_id, require_text, row_to_dict, utc_now


def create_visit(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = require_text(payload, "user_id")
    restaurant_id = require_text(payload, "restaurant_id")
    now = utc_now()
    visited_at = str(payload.get("visited_at") or now)
    visit_id = new_id()
    rating = payload.get("rating")
    if rating not in (None, ""):
        rating = clamp_int(rating, 0, 1, 5)
    else:
        rating = None

    with connect() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO visit_histories (
                  id, user_id, restaurant_id, search_log_id, rating, review_text,
                  is_verified, visited_at, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    visit_id,
                    user_id,
                    restaurant_id,
                    payload.get("search_log_id"),
                    rating,
                    payload.get("review_text"),
                    1 if payload.get("is_verified") else 0,
                    visited_at,
                    now,
                    now,
                ),
            )
            visit = conn.execute("SELECT * FROM visit_histories WHERE id = ?", (visit_id,)).fetchone()

            search_log_id = payload.get("search_log_id")
            if search_log_id:
                insert_recommendation_log(
                    conn,
                    search_log_id=search_log_id,
                    log_type="VISIT",
                    payload={"visit_id": visit_id, "request": payload},
                    now=now,
                )
    return {"visit": row_to_dict(visit)}


def list_visits(user_id: str, limit: int = 30) -> dict[str, Any]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
              vh.*,
              r.name AS restaurant_name,
              r.category AS restaurant_category,
              r.address AS restaurant_address
            FROM visit_histories vh
            JOIN restaurants r ON r.id = vh.restaurant_id
            WHERE vh.user_id = ?
            ORDER BY vh.visited_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return {"visits": [dict(row) for row in rows]}
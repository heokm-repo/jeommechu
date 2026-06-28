from __future__ import annotations

from typing import Any

try:
    from ..repositories.activity_repository import insert_recommendation_log
    from ..infra.database import connect
    from ..utils import new_id, utc_now
except ImportError:
    from repositories.activity_repository import insert_recommendation_log
    from infra.database import connect
    from utils import new_id, utc_now


def create_feedback(search_log_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    feedback_id = new_id()
    feedback = {
        "id": feedback_id,
        "user_id": payload.get("user_id"),
        "rating": payload.get("rating"),
        "comment": payload.get("comment") or payload.get("review_text"),
        "selected_restaurant_id": payload.get("restaurant_id"),
    }
    with connect() as conn:
        with conn:
            insert_recommendation_log(
                conn,
                search_log_id=search_log_id,
                log_type="FEEDBACK",
                payload=feedback,
                now=now,
                log_id=feedback_id,
            )
    return {"feedback": feedback}
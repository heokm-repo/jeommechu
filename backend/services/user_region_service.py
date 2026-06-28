from __future__ import annotations

from typing import Any

try:
    from ..infra.database import connect
    from ..utils import new_id, require_text, row_to_dict, utc_now
except ImportError:
    from infra.database import connect
    from utils import new_id, require_text, row_to_dict, utc_now


def create_region(payload: dict[str, Any]) -> dict[str, Any]:
    sido = require_text(payload, "sido")
    sigungu = require_text(payload, "sigungu")
    dong = require_text(payload, "dong")
    now = utc_now()
    region_id = new_id()
    with connect() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO regions (id, sido, sigungu, dong, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at)
                """,
                (region_id, sido, sigungu, dong, now, now),
            )
            row = conn.execute(
                "SELECT id, sido, sigungu, dong, created_at, updated_at FROM regions WHERE sido = ? AND sigungu = ? AND dong = ?",
                (sido, sigungu, dong),
            ).fetchone()
    return {"region": row_to_dict(row)}


def list_regions() -> dict[str, Any]:
    with connect() as conn:
        rows = conn.execute("SELECT id, sido, sigungu, dong, created_at, updated_at FROM regions ORDER BY created_at DESC").fetchall()
    return {"regions": [dict(row) for row in rows]}
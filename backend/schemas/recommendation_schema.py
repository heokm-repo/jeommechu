from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .base import bounded_int, optional_float, optional_text, required_text, string_list
except ImportError:
    from schemas.base import bounded_int, optional_float, optional_text, required_text, string_list


@dataclass(frozen=True)
class RecommendationSearchRequest:
    user_id: str | None
    emotion_state: str
    search_context: str
    contexts: list[str]
    address: str
    longitude: float | None
    latitude: float | None
    radius: int
    size: int
    query: str
    sort: str
    pages: int

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RecommendationSearchRequest":
        user_id = optional_text(payload, "user_id") or None
        return cls(
            user_id=user_id,
            emotion_state=required_text(payload, "emotion_state"),
            search_context=optional_text(payload, "search_context"),
            contexts=string_list(payload.get("contexts")),
            address=optional_text(payload, "address"),
            longitude=optional_float(payload, "longitude"),
            latitude=optional_float(payload, "latitude"),
            radius=bounded_int(payload, "radius", 1500, 1, 20000),
            size=bounded_int(payload, "size", 10, 1, 15),
            query=optional_text(payload, "query"),
            sort=optional_text(payload, "sort", "accuracy") or "accuracy",
            pages=bounded_int(payload, "pages", 3, 1, 3),
        )

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "emotion_state": self.emotion_state,
            "search_context": self.search_context,
            "contexts": self.contexts,
            "address": self.address,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "radius": self.radius,
            "size": self.size,
            "sort": self.sort,
            "pages": self.pages,
        }
        if self.query:
            payload["query"] = self.query
        return payload
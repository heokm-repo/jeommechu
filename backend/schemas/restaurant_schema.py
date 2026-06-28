from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .base import bounded_int, optional_float, optional_text
except ImportError:
    from schemas.base import bounded_int, optional_float, optional_text


@dataclass(frozen=True)
class RestaurantSearchRequest:
    query: str
    address: str
    longitude: float | None
    latitude: float | None
    radius: int
    size: int
    pages: int
    sort: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RestaurantSearchRequest":
        return cls(
            query=optional_text(payload, "query", "음식점") or "음식점",
            address=optional_text(payload, "address"),
            longitude=optional_float(payload, "longitude"),
            latitude=optional_float(payload, "latitude"),
            radius=bounded_int(payload, "radius", 1500, 1, 20000),
            size=bounded_int(payload, "size", 15, 1, 15),
            pages=bounded_int(payload, "pages", 3, 1, 3),
            sort=optional_text(payload, "sort", "accuracy") or "accuracy",
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "address": self.address,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "radius": self.radius,
            "size": self.size,
            "pages": self.pages,
            "sort": self.sort,
        }
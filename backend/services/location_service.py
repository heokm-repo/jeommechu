from __future__ import annotations

from typing import Any

try:
    from ..clients import geocode_address
    from ..utils import parse_float
except ImportError:
    from clients import geocode_address
    from utils import parse_float


def resolve_search_location(payload: dict[str, Any]) -> dict[str, Any]:
    """Resolve coordinates from user input, geocoding the address at most once."""
    address = str(payload.get("address") or "").strip()
    longitude = parse_float(payload.get("longitude"))
    latitude = parse_float(payload.get("latitude"))
    geocoded = None

    if (longitude is None or latitude is None) and address:
        geocoded = geocode_address(address)
        longitude = geocoded["longitude"]
        latitude = geocoded["latitude"]
        if longitude is None or latitude is None:
            raise ValueError(f"Geocoding did not return coordinates for address: {address}")

    return {
        "address": address,
        "longitude": longitude,
        "latitude": latitude,
        "geocoded": geocoded,
    }

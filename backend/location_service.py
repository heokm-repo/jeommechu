from __future__ import annotations

try:
    from .services.location_service import *
except ImportError:
    from services.location_service import *
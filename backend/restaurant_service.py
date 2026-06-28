from __future__ import annotations

try:
    from .services.restaurant_service import *
except ImportError:
    from services.restaurant_service import *
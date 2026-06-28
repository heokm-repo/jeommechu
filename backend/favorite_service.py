from __future__ import annotations

try:
    from .services.favorite_service import *
except ImportError:
    from services.favorite_service import *
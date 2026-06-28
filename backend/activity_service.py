from __future__ import annotations

try:
    from .services.activity_service import *
except ImportError:
    from services.activity_service import *
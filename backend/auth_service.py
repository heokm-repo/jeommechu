from __future__ import annotations

try:
    from .services.auth_service import *
except ImportError:
    from services.auth_service import *
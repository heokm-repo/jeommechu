from __future__ import annotations

try:
    from .repositories.restaurant_repository import *
except ImportError:
    from repositories.restaurant_repository import *
from __future__ import annotations

try:
    from .repositories.activity_repository import *
except ImportError:
    from repositories.activity_repository import *
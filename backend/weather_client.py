from __future__ import annotations

try:
    from .clients.weather_client import *
except ImportError:
    from clients.weather_client import *
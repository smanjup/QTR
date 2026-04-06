"""ASGI entry for Vercel — export `app` (required by Vercel Python runtime)."""

from __future__ import annotations

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(_backend))

from main import app  # noqa: E402

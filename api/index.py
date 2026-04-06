"""ASGI entry for Vercel — Fractal Lab API (FastAPI in fractal-lab/backend)."""

from __future__ import annotations

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent / "fractal-lab" / "backend"
sys.path.insert(0, str(_backend))

from main import app  # noqa: E402

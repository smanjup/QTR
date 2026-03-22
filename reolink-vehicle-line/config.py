"""Configuration loader for Reolink vehicle-line application."""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_PATH}\n"
            "Copy config.example.json to config.json and fill in your camera details."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_config(
    ip: str | None = None,
    user: str | None = None,
    password: str | None = None,
    channel: int | None = None,
    stream: str | None = None,
    line_y_ratio: float | None = None,
) -> dict:
    try:
        data = load_config()
    except FileNotFoundError:
        data = {}

    cfg_line = data.get("line_y_ratio", 0.6)
    if line_y_ratio is not None:
        cfg_line = line_y_ratio

    return {
        "ip": ip or data.get("ip"),
        "user": user or data.get("user", "admin"),
        "password": password or os.environ.get("REOLINK_PASSWORD") or data.get("password"),
        "channel": data.get("channel", 1) if channel is None else channel,
        "stream": data.get("stream", "sub") if stream is None else stream,
        "line_y_ratio": float(cfg_line),
        "confidence": float(data.get("confidence", 0.5)),
        "model_size": str(data.get("model_size", "n")),
    }

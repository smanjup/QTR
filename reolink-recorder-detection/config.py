"""Configuration loader for Reolink camera settings."""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    """Load config from config.json. Returns dict with ip, user, password, channel, stream."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_PATH}\n"
            "Copy config.example.json to config.json and fill in your camera details."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_config(
    ip: str | None = None,
    user: str | None = None,
    password: str | None = None,
    channel: int | None = None,
    stream: str | None = None,
) -> dict:
    """
    Load config from file, with optional overrides from arguments or env vars.
    Password can be overridden by REOLINK_PASSWORD env var.
    """
    try:
        data = load_config()
    except FileNotFoundError:
        data = {}

    cfg = {
        "ip": ip or data.get("ip"),
        "user": user or data.get("user", "admin"),
        "password": password or os.environ.get("REOLINK_PASSWORD") or data.get("password"),
        "channel": data.get("channel", 1) if channel is None else channel,
        "stream": data.get("stream", "sub") if stream is None else stream,
    }
    return cfg

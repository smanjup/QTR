"""Load config from reolink-recorder-detection/config.json."""

import json
import os
from pathlib import Path

# Config is shared with desktop app
CONFIG_PATH = Path(__file__).parent.parent.parent / "reolink-recorder-detection" / "config.json"


def load_config() -> dict:
    """Load config from config.json."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_PATH}\n"
            "Copy reolink-recorder-detection/config.example.json to config.json."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_config() -> dict:
    """Load config with env var override for password."""
    data = load_config()
    return {
        "ip": data["ip"],
        "user": data.get("user", "admin"),
        "password": os.environ.get("REOLINK_PASSWORD") or data.get("password"),
        "channel": data.get("channel", 1),
        "stream": data.get("stream", "sub"),
    }

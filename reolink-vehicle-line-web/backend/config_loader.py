"""Load config from reolink-vehicle-line/config.json."""

import json
import os
from pathlib import Path

CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "reolink-vehicle-line" / "config.json"
)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Config not found: {CONFIG_PATH}\nCopy reolink-vehicle-line/config.example.json to config.json"
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_config() -> dict:
    data = load_config()
    return {
        "ip": data.get("ip"),
        "user": data.get("user", "admin"),
        "password": os.environ.get("REOLINK_PASSWORD") or data.get("password"),
        "channel": data.get("channel", 1),
        "stream": data.get("stream", "sub"),
        "line_y_ratio": float(data.get("line_y_ratio", 0.6)),
        "confidence": float(data.get("confidence", 0.5)),
        "model_size": str(data.get("model_size", "n")),
    }

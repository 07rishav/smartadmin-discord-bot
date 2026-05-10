"""Small helpers for loading and saving the bot JSON config."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "guild_id": 0,
    "log_channel_id": 0,
    "welcome_channel_id": 0,
    "goodbye_channel_id": 0,
    "ticket_category_id": 0,
    "moderator_role_id": 0,
    "muted_role_id": 0,
    "secret_role_id": 0,
    "secret_role_password": "change-me",
    "bad_words": [],
    "reaction_roles": {},
}


def _deep_merge(defaults: dict[str, Any], loaded: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(defaults)
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """Load config.json and fill in any missing keys with defaults."""

    if not path.exists():
        save_config(DEFAULT_CONFIG, path)
        return deepcopy(DEFAULT_CONFIG)

    with path.open("r", encoding="utf-8") as config_file:
        loaded = json.load(config_file)

    if not isinstance(loaded, dict):
        raise ValueError("config.json must contain a JSON object.")

    # Keep older config files working when new optional settings are added.
    return _deep_merge(DEFAULT_CONFIG, loaded)


def save_config(config: dict[str, Any], path: Path = CONFIG_PATH) -> None:
    """Persist config changes made by slash commands."""

    path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def get_config_id(config: dict[str, Any], key: str) -> int | None:
    """Return a snowflake ID from config, treating 0/empty values as unset."""

    value = config.get(key)
    if value in (None, "", 0, "0"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

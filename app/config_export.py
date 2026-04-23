"""Config export with optional secrets masking and clipboard support."""

import json
import tkinter as tk
from pathlib import Path
from typing import Any


_DEFAULT_MASK_PATTERNS = [
    "API_KEY", "KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL",
]


def _contains_secret(value: str, patterns: list[str]) -> bool:
    upper = value.upper()
    for pat in patterns:
        if pat.upper() in upper:
            return True
    return False


def _mask_value(value: str, patterns: list[str]) -> str:
    if _contains_secret(value, patterns):
        return "***REDACTED***"
    return value


def _mask_config(data: dict[str, Any], patterns: list[str]) -> dict[str, Any]:
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = _mask_value(value, patterns)
        elif isinstance(value, dict):
            result[key] = _mask_config(value, patterns)
        elif isinstance(value, list):
            result[key] = [
                _mask_value(item, patterns) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


class SecretsMasker:
    def __init__(self, patterns: list[str] | None = None):
        self.patterns = patterns or _DEFAULT_MASK_PATTERNS

    def mask(self, data: dict[str, Any]) -> dict[str, Any]:
        return _mask_config(data, self.patterns)


def export_to_json(data: dict[str, Any]) -> str:
    ordered = _order_schema_first(data)
    return json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"


def _order_schema_first(data: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    if "$schema" in data:
        ordered["$schema"] = data["$schema"]
    for key, value in data.items():
        if key != "$schema":
            ordered[key] = value
    return ordered


def export_to_file(
    data: dict[str, Any],
    file_path: str | Path,
    *,
    masker: SecretsMasker | None = None,
) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    to_save = masker.mask(data) if masker else data
    text = export_to_json(to_save)
    path.write_text(text, encoding="utf-8")


def export_to_clipboard(
    data: dict[str, Any],
    *,
    masker: SecretsMasker | None = None,
) -> str:
    to_save = masker.mask(data) if masker else data
    text = export_to_json(to_save)
    try:
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
    except Exception:
        try:
            import pyperclip
            pyperclip.copy(text)
        except Exception:
            pass
    return text

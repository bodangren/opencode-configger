"""Config import with validation, merge strategies, and clipboard support."""

import json
from pathlib import Path
from typing import Any

from app.config_io import strip_jsonc_comments
from app.config_schema import validate_config, get_nested


class ImportValidationError(Exception):
    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []
        self.message = message


class ImportResult:
    def __init__(
        self,
        data: dict[str, Any],
        errors: list[str],
        unknown_keys: list[str],
    ):
        self.data = data
        self.errors = errors
        self.unknown_keys = unknown_keys
        self.is_valid = len(errors) == 0 and len(unknown_keys) == 0


def _detect_jsonc(text: str) -> bool:
    return "/*" in text or "//" in text


def import_from_text(
    text: str,
    *,
    validate: bool = True,
    allow_unknown_keys: bool = False,
) -> ImportResult:
    clean = strip_jsonc_comments(text)
    if not clean.strip():
        return ImportResult({}, [], [])

    try:
        data = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise ImportValidationError(
            f"JSON parse error at line {exc.lineno}, col {exc.colno}: {exc.msg}",
            errors=[f"JSON parse error: {exc.msg}"],
        ) from exc

    if not isinstance(data, dict):
        raise ImportValidationError("Config must be a JSON object", errors=["Config must be a JSON object"])

    unknown_keys = _find_unknown_keys(data) if not allow_unknown_keys else []
    errors: list[str] = []
    if validate:
        errors = validate_config(data)

    return ImportResult(data, errors, unknown_keys)


def import_from_file(
    file_path: str | Path,
    *,
    validate: bool = True,
    allow_unknown_keys: bool = False,
) -> ImportResult:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    text = path.read_text(encoding="utf-8")
    return import_from_text(text, validate=validate, allow_unknown_keys=allow_unknown_keys)


def import_from_clipboard(
    *,
    validate: bool = True,
    allow_unknown_keys: bool = False,
) -> ImportResult:
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.update()
        try:
            text = root.clipboard_get()
        except Exception:
            text = ""
        finally:
            root.destroy()
    except Exception:
        try:
            import pyperclip
            text = pyperclip.paste()
        except Exception:
            text = ""
    if not text.strip():
        return ImportResult({}, [], [])
    return import_from_text(text, validate=validate, allow_unknown_keys=allow_unknown_keys)


_VALID_TOP_LEVEL_KEYS = {
    "$schema", "model", "small_model", "default_agent", "logLevel",
    "username", "share", "autoupdate", "snapshot",
    "server", "compaction", "watcher", "instructions", "plugin",
    "skills", "provider", "agent", "permission", "command",
    "formatter", "mcp", "lsp", "experimental", "enterprise",
    "tui",
}


def _find_unknown_keys(data: dict[str, Any]) -> list[str]:
    unknown = []
    for key in data.keys():
        if key not in _VALID_TOP_LEVEL_KEYS:
            unknown.append(key)
    return unknown


class MergeStrategy:
    REPLACE = "replace"
    OVERLAY = "overlay"
    SELECTIVE = "selective"


def merge_replace(current: dict[str, Any], imported: dict[str, Any]) -> dict[str, Any]:
    return imported.copy()


def merge_overlay(current: dict[str, Any], imported: dict[str, Any]) -> dict[str, Any]:
    result = _deep_copy(current)
    _deep_merge(result, imported)
    return result


def _deep_copy(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _deep_copy(value)
        elif isinstance(value, list):
            result[key] = value.copy()
        else:
            result[key] = value
    return result


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> None:
    for key, value in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = _deep_copy(value) if isinstance(value, dict) else value


def merge_selective(
    current: dict[str, Any],
    imported: dict[str, Any],
    accept_keys: set[str],
) -> dict[str, Any]:
    result = _deep_copy(current)
    for key in accept_keys:
        if key in imported:
            result[key] = _deep_copy(imported[key]) if isinstance(imported[key], dict) else imported[key]
    return result


def compute_diff(
    current: dict[str, Any],
    imported: dict[str, Any],
) -> dict[str, tuple[Any, Any]]:
    diff: dict[str, tuple[Any, Any]] = {}
    all_keys = set(current.keys()) | set(imported.keys())
    for key in all_keys:
        cur_val = current.get(key)
        imp_val = imported.get(key)
        if cur_val != imp_val:
            diff[key] = (cur_val, imp_val)
    return diff

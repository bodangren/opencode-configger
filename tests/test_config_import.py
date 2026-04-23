"""Tests for config import module."""

import json
from pathlib import Path

import pytest

from app.config_import import (
    ImportResult,
    ImportValidationError,
    MergeStrategy,
    _find_unknown_keys,
    _detect_jsonc,
    compute_diff,
    import_from_file,
    import_from_text,
    merge_overlay,
    merge_replace,
    merge_selective,
)


def test_detect_jsonc_with_comments() -> None:
    assert _detect_jsonc("// comment\n{}") is True
    assert _detect_jsonc("/* block */ {}") is True


def test_detect_jsonc_pure_json() -> None:
    assert _detect_jsonc('{"key": "value"}') is False


def test_import_from_text_valid_json() -> None:
    text = '{"model": "openai/gpt-4"}'
    result = import_from_text(text, validate=False)
    assert result.data == {"model": "openai/gpt-4"}
    assert result.is_valid is True


def test_import_from_text_valid_jsonc() -> None:
    text = '''
    {
      // my model
      "model": "anthropic/claude-3.7-sonnet",
      "snapshot": true,
    }
    '''
    result = import_from_text(text, validate=False)
    assert result.data["model"] == "anthropic/claude-3.7-sonnet"
    assert result.is_valid is True


def test_import_from_text_trailing_comma() -> None:
    text = '{"items": [1, 2, 3,],}'
    result = import_from_text(text, validate=False)
    assert result.data == {"items": [1, 2, 3]}


def test_import_from_text_invalid_json() -> None:
    text = '{"model": }'
    with pytest.raises(ImportValidationError):
        import_from_text(text, validate=False)


def test_import_from_text_empty() -> None:
    result = import_from_text("", validate=False)
    assert result.data == {}
    assert result.is_valid is True


def test_import_from_text_unknown_keys() -> None:
    text = '{"model": "openai/gpt-4", "unknown_key": "value"}'
    result = import_from_text(text, validate=False, allow_unknown_keys=False)
    assert "unknown_key" in result.unknown_keys
    assert result.is_valid is False


def test_import_from_text_allow_unknown_keys() -> None:
    text = '{"model": "openai/gpt-4", "unknown_key": "value"}'
    result = import_from_text(text, validate=False, allow_unknown_keys=True)
    assert result.is_valid is True


def test_import_from_text_with_validation_errors(tmp_path: Path) -> None:
    text = '{"logLevel": "INVALID_LEVEL"}'
    result = import_from_text(text, validate=True)
    assert result.is_valid is False
    assert len(result.errors) > 0


def test_import_from_file(tmp_path: Path) -> None:
    path = tmp_path / "test_config.json"
    path.write_text('{"model": "openai/gpt-4"}', encoding="utf-8")
    result = import_from_file(path, validate=False)
    assert result.data["model"] == "openai/gpt-4"


def test_import_from_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        import_from_file("/nonexistent/path.json", validate=False)


def test_merge_replace() -> None:
    current = {"model": "old-model", "snapshot": False}
    imported = {"model": "new-model"}
    result = merge_replace(current, imported)
    assert result == {"model": "new-model"}
    assert current == {"model": "old-model", "snapshot": False}


def test_merge_overlay_nested() -> None:
    current = {
        "server": {"port": 8080, "hostname": "localhost"},
        "model": "old",
    }
    imported = {
        "server": {"port": 9000},
        "model": "new",
    }
    result = merge_overlay(current, imported)
    assert result["server"]["port"] == 9000
    assert result["server"]["hostname"] == "localhost"
    assert result["model"] == "new"


def test_merge_overlay_does_not_mutate_inputs() -> None:
    current = {"model": "old"}
    imported = {"model": "new"}
    merge_overlay(current, imported)
    assert current["model"] == "old"
    assert imported["model"] == "new"


def test_merge_selective() -> None:
    current = {"model": "old", "snapshot": True}
    imported = {"model": "new", "logLevel": "DEBUG"}
    result = merge_selective(current, imported, accept_keys={"model"})
    assert result["model"] == "new"
    assert result["snapshot"] is True
    assert "logLevel" not in result


def test_compute_diff() -> None:
    current = {"model": "old", "extra": "kept"}
    imported = {"model": "new", "added": "value"}
    diff = compute_diff(current, imported)
    assert diff["model"] == ("old", "new")
    assert "extra" in diff
    assert diff["extra"] == ("kept", None)
    assert "added" in diff
    assert diff["added"] == (None, "value")


def test_find_unknown_keys() -> None:
    data = {"model": "x", "unknown_top": "y"}
    unknown = _find_unknown_keys(data)
    assert "unknown_top" in unknown
    assert "model" not in unknown

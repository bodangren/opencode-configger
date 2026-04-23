"""Tests for config export module."""

import json
import re
from pathlib import Path

import pytest

from app.config_export import (
    SecretsMasker,
    _DEFAULT_MASK_PATTERNS,
    _mask_config,
    _mask_value,
    export_to_clipboard,
    export_to_file,
    export_to_json,
)


def test_mask_value_matches_default_patterns() -> None:
    for val in ["API_KEY=abc", "my_token_123", "secret_value", "PASSWORD"]:
        assert _mask_value(val, _DEFAULT_MASK_PATTERNS) == "***REDACTED***"


def test_mask_value_ignores_non_matching() -> None:
    for val in ["model", "openai/gpt-4", "username"]:
        assert _mask_value(val, _DEFAULT_MASK_PATTERNS) == val


def test_mask_config_nested() -> None:
    data = {
        "provider": {
            "openai": {
                "options": {"apiKey": "sk-secret123"},
            }
        }
    }
    masked = _mask_config(data, _DEFAULT_MASK_PATTERNS)
    assert masked["provider"]["openai"]["options"]["apiKey"] == "***REDACTED***"


def test_mask_config_list() -> None:
    data = {"plugins": ["@opencode/api-key-plugin", "some-plugin"]}
    masked = _mask_config(data, _DEFAULT_MASK_PATTERNS)
    assert masked["plugins"][0] == "***REDACTED***"
    assert masked["plugins"][1] == "some-plugin"


def test_mask_config_preserves_non_string() -> None:
    data = {"port": 8080, "enabled": True}
    masked = _mask_config(data, _DEFAULT_MASK_PATTERNS)
    assert masked == data


def test_secrets_masker_default_patterns() -> None:
    masker = SecretsMasker()
    data = {"apiKey": "API_KEY=sk-12345", "model": "openai/gpt-4"}
    masked = masker.mask(data)
    assert masked["apiKey"] == "***REDACTED***"
    assert masked["model"] == "openai/gpt-4"


def test_secrets_masker_custom_patterns() -> None:
    masker = SecretsMasker(patterns=["MYAPP"])
    data = {"apiKey": "myapp_token_xyz", "model": "openai/gpt-4"}
    masked = masker.mask(data)
    assert masked["apiKey"] == "***REDACTED***"
    assert masked["model"] == "openai/gpt-4"


def test_export_to_json_schema_first(tmp_path: Path) -> None:
    data = {
        "model": "anthropic/claude-3.7-sonnet",
        "$schema": "https://opencode.ai/config.json",
        "snapshot": True,
    }
    text = export_to_json(data)
    lines = text.splitlines()
    assert '$schema' in lines[1]


def test_export_to_file(tmp_path: Path) -> None:
    data = {"model": "openai/gpt-4", "$schema": "https://opencode.ai/config.json"}
    path = tmp_path / "exported.json"
    export_to_file(data, path)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["model"] == "openai/gpt-4"


def test_export_to_file_with_masking(tmp_path: Path) -> None:
    data = {
        "provider": {
            "openai": {"options": {"apiKey": "sk-secret"}}
        }
    }
    masker = SecretsMasker()
    path = tmp_path / "masked.json"
    export_to_file(data, path, masker=masker)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["provider"]["openai"]["options"]["apiKey"] == "***REDACTED***"


def test_export_to_clipboard_returns_text() -> None:
    data = {"model": "openai/gpt-4", "$schema": "https://opencode.ai/config.json"}
    text = export_to_clipboard(data)
    assert "openai/gpt-4" in text
    assert "$schema" in text

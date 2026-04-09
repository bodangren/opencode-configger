"""Tests for config JSONC file I/O helpers."""

import os
from pathlib import Path

import pytest

from app.config_io import (
    VariableResolutionError,
    find_config_files,
    find_variables,
    load_jsonc,
    new_config,
    new_tui_config,
    preview_variable,
    resolve_env_var,
    resolve_file_var,
    save_json,
    strip_jsonc_comments,
    substitute_variables,
)


def test_strip_jsonc_comments_and_trailing_commas() -> None:
    source = """
    {
      // single line
      "key": "value // not a comment",
      "items": [1, 2,],
      /* block comment */
      "enabled": true,
    }
    """
    cleaned = strip_jsonc_comments(source)
    assert "single line" not in cleaned
    assert "block comment" not in cleaned
    assert '"value // not a comment"' in cleaned
    assert ",]" not in cleaned
    assert ",}" not in cleaned


def test_load_jsonc_parses_file_with_comments(tmp_path: Path) -> None:
    path = tmp_path / "opencode.json"
    path.write_text(
        '{\n  // comment\n  "model": "openai/gpt-4",\n  "snapshot": true\n}\n',
        encoding="utf-8",
    )

    loaded = load_jsonc(path)
    assert loaded == {"model": "openai/gpt-4", "snapshot": True}


def test_load_jsonc_empty_file_returns_empty_dict(tmp_path: Path) -> None:
    path = tmp_path / "empty.json"
    path.write_text("\n/* no config yet */\n", encoding="utf-8")
    assert load_jsonc(path) == {}


def test_save_json_writes_schema_first(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    data = {
        "model": "anthropic/claude-3.7-sonnet",
        "$schema": "https://opencode.ai/config.json",
        "snapshot": True,
    }

    save_json(path, data)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert '  "$schema": "https://opencode.ai/config.json",' in lines[1]


def test_find_config_files_returns_expected_locations(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    fake_cwd = tmp_path / "project"
    fake_cwd.mkdir()

    global_file = fake_home / ".config" / "opencode" / "opencode.json"
    global_file.parent.mkdir(parents=True)
    global_file.write_text("{}", encoding="utf-8")

    project_file = fake_cwd / "opencode.json"
    project_file.write_text("{}", encoding="utf-8")

    env_file = tmp_path / "env-config.json"
    env_file.write_text("{}", encoding="utf-8")

    tui_file = fake_home / ".config" / "opencode" / "tui.json"
    tui_file.write_text("{}", encoding="utf-8")

    monkeypatch.setenv("OPENCODE_CONFIG", str(env_file))
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.chdir(fake_cwd)

    found = find_config_files()
    assert found["global"] == global_file
    assert found["project"] == project_file
    assert found["env"] == env_file
    assert found["tui_global"] == tui_file


def test_new_config_helpers_return_schema_defaults() -> None:
    assert new_config() == {"$schema": "https://opencode.ai/config.json"}
    assert new_tui_config() == {"$schema": "https://opencode.ai/tui.json"}


def test_resolve_env_var_existing(monkeypatch) -> None:
    monkeypatch.setenv("MY_TEST_VAR", "my_test_value")
    assert resolve_env_var("MY_TEST_VAR") == "my_test_value"


def test_resolve_env_var_missing_raises() -> None:
    with pytest.raises(VariableResolutionError, match="not set"):
        resolve_env_var("DEFINITELY_NOT_A_REAL_ENV_VAR_12345")


def test_resolve_file_var(tmp_path: Path) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("file contents here", encoding="utf-8")
    assert resolve_file_var(str(file_path)) == "file contents here"


def test_resolve_file_var_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(VariableResolutionError, match="File not found"):
        resolve_file_var(str(tmp_path / "does_not_exist.txt"))


def test_resolve_file_var_truncates_large_file(tmp_path: Path) -> None:
    file_path = tmp_path / "large.txt"
    file_path.write_text("x" * 2000, encoding="utf-8")
    result = resolve_file_var(str(file_path))
    assert len(result) < 2000
    assert result.endswith("[truncated]")


def test_substitute_variables_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MY_HOME", "/home/testuser")
    result = substitute_variables("home is {env:MY_HOME}")
    assert result == "home is /home/testuser"


def test_substitute_variables_file(tmp_path: Path) -> None:
    file_path = tmp_path / "myfile.txt"
    file_path.write_text("secret content", encoding="utf-8")
    result = substitute_variables("file contents: {file:myfile.txt}", base_path=tmp_path)
    assert result == "file contents: secret content"


def test_find_variables() -> None:
    text = "model: {env:MODEL}, config: {file:./config.json}"
    found = find_variables(text)
    assert ("env", "MODEL") in found
    assert ("file", "./config.json") in found


def test_preview_variable_env(monkeypatch) -> None:
    monkeypatch.setenv("PREVIEW_TEST", "preview_value")
    result = preview_variable("setting is {env:PREVIEW_TEST}")
    assert result["{env:PREVIEW_TEST}"] == "preview_value"


def test_preview_variable_missing_env(monkeypatch) -> None:
    monkeypatch.delenv("NONEXISTENT_VAR_12345", raising=False)
    result = preview_variable("setting is {env:NONEXISTENT_VAR_12345}")
    assert "ERROR" in result["{env:NONEXISTENT_VAR_12345}"]


def test_preview_variable_file(tmp_path: Path) -> None:
    file_path = tmp_path / "preview_test.txt"
    file_path.write_text("preview content", encoding="utf-8")
    result = preview_variable("{file:preview_test.txt}", base_path=tmp_path)
    assert result["{file:preview_test.txt}"] == "preview content"


def test_preview_variable_no_variables() -> None:
    result = preview_variable("just a plain string")
    assert result == {}

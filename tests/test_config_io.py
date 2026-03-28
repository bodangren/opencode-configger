"""Tests for config JSONC file I/O helpers."""

from pathlib import Path

from app.config_io import (
    find_config_files,
    load_jsonc,
    new_config,
    new_tui_config,
    save_json,
    strip_jsonc_comments,
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

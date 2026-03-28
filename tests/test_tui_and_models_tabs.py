"""Tests for TUI and model browser tabs."""

import tkinter as tk

import pytest

from app.tabs.models import ModelsTab, parse_models_json, parse_models_text
from app.tabs.tui import KeybindEditor, TuiTab


@pytest.fixture
def tk_root() -> tk.Tk:
    """Create a Tk root window for GUI tests."""
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    root.withdraw()
    yield root
    root.destroy()


def test_tui_tab_load_and_save_roundtrip(tk_root: tk.Tk) -> None:
    tab = TuiTab(tk_root)
    source = {
        "$schema": "https://opencode.ai/tui.json",
        "theme": "tokyonight",
        "scroll_speed": 1.25,
        "diff_style": "stacked",
        "scroll_acceleration": {"enabled": True},
        "keybinds": {
            "leader": "ctrl+k",
            "app_exit": "ctrl+q",
        },
    }

    tab.load_config(source)
    output: dict = {}
    tab.save_config(output)

    assert output["$schema"] == "https://opencode.ai/tui.json"
    assert output["theme"] == "tokyonight"
    assert output["scroll_speed"] == 1.25
    assert output["diff_style"] == "stacked"
    assert output["scroll_acceleration"]["enabled"] is True
    assert output["keybinds"]["leader"] == "ctrl+k"


def test_keybind_editor_search_and_edit(tk_root: tk.Tk) -> None:
    editor = KeybindEditor(tk_root)
    editor.set_value({"leader": "ctrl+k"})

    editor.search_var.set("leader")
    assert editor.slot_list.size() >= 1
    editor.slot_list.selection_set(0)
    editor._on_slot_selected(None)
    editor.value_var.set("ctrl+space")

    values = editor.get_value()
    assert values is not None
    assert values["leader"] == "ctrl+space"


def test_parse_models_json_accepts_list_and_mapping() -> None:
    raw_list = '["openai/gpt-4.1", "anthropic/claude-3.7-sonnet"]'
    parsed_list = parse_models_json(raw_list)
    assert parsed_list["openai"] == ["openai/gpt-4.1"]
    assert parsed_list["anthropic"] == ["anthropic/claude-3.7-sonnet"]

    raw_map = '{"openai": ["openai/gpt-4.1", "openai/gpt-4.1-mini"]}'
    parsed_map = parse_models_json(raw_map)
    assert parsed_map["openai"] == ["openai/gpt-4.1", "openai/gpt-4.1-mini"]


def test_parse_models_text_extracts_provider_and_model() -> None:
    raw = """
    Available models:
    - openai/gpt-4.1
    - openai/gpt-4.1-mini
    - anthropic/claude-3.7-sonnet
    """
    parsed = parse_models_text(raw)
    assert "openai" in parsed
    assert "openai/gpt-4.1" in parsed["openai"]
    assert "anthropic/claude-3.7-sonnet" in parsed["anthropic"]


def test_models_tab_selection_callback(tk_root: tk.Tk) -> None:
    chosen: list[tuple[str, str]] = []

    def on_pick(model: str, target: str) -> None:
        chosen.append((model, target))

    tab = ModelsTab(tk_root, on_pick_model=on_pick, auto_refresh=False)
    tab.models = {"openai": ["openai/gpt-4.1"]}
    tab._populate_tree()

    provider_id = tab.tree.get_children()[0]
    model_id = tab.tree.get_children(provider_id)[0]
    tab.tree.selection_set(model_id)
    tab._update_selection()
    tab._apply_selection("small_model")

    assert chosen == [("openai/gpt-4.1", "small_model")]

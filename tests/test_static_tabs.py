"""Tests for static configuration tabs."""

import tkinter as tk

import pytest

from app.tabs.compaction import AdvancedTab
from app.tabs.general import GeneralTab
from app.tabs.server import ServerTab
from app.widgets import SectionFrame


@pytest.fixture
def tk_root() -> tk.Tk:
    """Create a Tk root window for tab tests."""
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    root.withdraw()
    yield root
    root.destroy()


def test_general_tab_load_and_save_config(tk_root: tk.Tk) -> None:
    tab = GeneralTab(tk_root)
    source = {
        "model": "openai/gpt-4.1",
        "small_model": "openai/gpt-4.1-mini",
        "default_agent": "build",
        "logLevel": "INFO",
        "username": "daniel",
        "share": "manual",
        "autoupdate": "notify",
        "snapshot": True,
    }

    tab.load_config(source)
    output: dict = {}
    tab.save_config(output)

    assert output["model"] == source["model"]
    assert output["small_model"] == source["small_model"]
    assert output["default_agent"] == source["default_agent"]
    assert output["logLevel"] == source["logLevel"]
    assert output["username"] == source["username"]
    assert output["share"] == source["share"]
    assert output["autoupdate"] == "notify"
    assert output["snapshot"] is True


def test_general_tab_autoupdate_bool_coercion(tk_root: tk.Tk) -> None:
    tab = GeneralTab(tk_root)
    tab.widgets["autoupdate"].set_value("true")

    output: dict = {}
    tab.save_config(output)

    assert output["autoupdate"] is True


def test_server_tab_save_and_remove_empty_section(tk_root: tk.Tk) -> None:
    tab = ServerTab(tk_root)

    tab.widgets["port"].set_value("8080")
    tab.widgets["hostname"].set_value("0.0.0.0")
    tab.widgets["mdns"].set_value(True)
    tab.widgets["mdnsDomain"].set_value("dev.local")
    tab.widgets["cors"].set_value(["http://localhost:3000"])

    output: dict = {}
    tab.save_config(output)

    assert output["server"]["port"] == 8080
    assert output["server"]["hostname"] == "0.0.0.0"
    assert output["server"]["mdns"] is True
    assert output["server"]["mdnsDomain"] == "dev.local"
    assert output["server"]["cors"] == ["http://localhost:3000"]

    empty_tab = ServerTab(tk_root)
    output_with_existing = {"server": {"port": 4096}}
    empty_tab.save_config(output_with_existing)
    assert "server" not in output_with_existing


def test_advanced_tab_load_and_save_multiple_sections(tk_root: tk.Tk) -> None:
    tab = AdvancedTab(tk_root)

    source = {
        "compaction": {"auto": False, "prune": True, "reserved": 2048},
        "watcher": {"ignore": [".git", "node_modules"]},
        "instructions": [".opencode/INSTRUCTIONS.md"],
        "plugin": ["@company/opencode-plugin"],
        "skills": {
            "paths": ["./skills"],
            "urls": ["https://example.com/skills.json"],
        },
        "disabled_providers": ["xai"],
        "enabled_providers": ["openai", "anthropic"],
    }

    tab.load_config(source)
    output: dict = {}
    tab.save_config(output)

    assert output["compaction"]["auto"] is False
    assert output["compaction"]["prune"] is True
    assert output["compaction"]["reserved"] == 2048
    assert output["watcher"]["ignore"] == [".git", "node_modules"]
    assert output["instructions"] == [".opencode/INSTRUCTIONS.md"]
    assert output["plugin"] == ["@company/opencode-plugin"]
    assert output["skills"]["paths"] == ["./skills"]
    assert output["skills"]["urls"] == ["https://example.com/skills.json"]
    assert output["disabled_providers"] == ["xai"]
    assert output["enabled_providers"] == ["openai", "anthropic"]


def test_section_frame_collapse_and_expand(tk_root: tk.Tk) -> None:
    section = SectionFrame(tk_root, text="Test Section")
    section.pack()
    assert not section.collapsed

    section.toggle()
    assert section.collapsed

    section.toggle()
    assert not section.collapsed


def test_section_frame_starts_collapsed(tk_root: tk.Tk) -> None:
    section = SectionFrame(tk_root, text="Collapsed", collapsed=True)
    section.pack()
    assert section.collapsed


def test_smoke_all_tabs_render(tk_root: tk.Tk) -> None:
    """Smoke test: all tabs instantiate without error."""
    from tkinter import ttk as ttk_mod
    from app.tabs.agents import AgentsTab
    from app.tabs.commands import CommandsTab
    from app.tabs.formatters import FormattersTab
    from app.tabs.mcp import MCPServersTab
    from app.tabs.providers import ProvidersTab
    from app.tabs.tools import ToolsTab
    from app.tabs.tui import TuiTab

    nb = ttk_mod.Notebook(tk_root)
    nb.pack()

    tabs = [
        GeneralTab(nb),
        ServerTab(nb),
        AdvancedTab(nb),
        ProvidersTab(nb),
        AgentsTab(nb),
        ToolsTab(nb),
        CommandsTab(nb),
        FormattersTab(nb),
        MCPServersTab(nb),
        TuiTab(nb),
    ]
    for i, tab in enumerate(tabs):
        nb.add(tab, text=f"Tab{i}")

    tk_root.update_idletasks()
    assert nb.index("end") == len(tabs)

"""Tests for dynamic configuration tabs."""

import tkinter as tk

import pytest

from app.tabs.agents import AgentsTab
from app.tabs.commands import CommandsTab
from app.tabs.formatters import FormattersTab
from app.tabs.lsp import LSPTab
from app.tabs.mcp import MCPServersTab
from app.tabs.providers import ProvidersTab
from app.tabs.tools import ToolsTab


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


def test_providers_tab_load_and_save(tk_root: tk.Tk) -> None:
    tab = ProvidersTab(tk_root)
    source = {
        "provider": {
            "openai": {
                "options": {"baseURL": "https://api.openai.com", "timeout": 300000},
                "disabled": False,
            }
        }
    }
    tab.load_config(source)

    output: dict = {}
    tab.save_config(output)

    assert "provider" in output
    assert output["provider"]["openai"]["options"]["baseURL"] == "https://api.openai.com"


def test_agents_tab_load_and_save(tk_root: tk.Tk) -> None:
    tab = AgentsTab(tk_root)
    source = {
        "agent": {
            "planner": {
                "model": "openai/gpt-4.1",
                "description": "Plans implementation",
                "mode": "subagent",
                "hidden": False,
                "disable": False,
                "steps": 20,
            }
        }
    }
    tab.load_config(source)

    output: dict = {}
    tab.save_config(output)

    assert "agent" in output
    assert output["agent"]["planner"]["mode"] == "subagent"


def test_tools_tab_load_and_save(tk_root: tk.Tk) -> None:
    tab = ToolsTab(tk_root)
    source = {
        "permission": {
            "read": "allow",
            "edit": "ask",
            "bash": "deny",
        }
    }
    tab.load_config(source)

    output: dict = {}
    tab.save_config(output)

    assert output["permission"]["read"] == "allow"
    assert output["permission"]["edit"] == "ask"
    assert output["permission"]["bash"] == "deny"


def test_commands_tab_load_and_save(tk_root: tk.Tk) -> None:
    tab = CommandsTab(tk_root)
    source = {
        "command": {
            "summarize": {
                "template": "Summarize the current diff",
                "description": "Summarize changes",
                "agent": "planner",
                "model": "openai/gpt-4.1",
            }
        }
    }
    tab.load_config(source)

    output: dict = {}
    tab.save_config(output)

    assert "command" in output
    assert output["command"]["summarize"]["template"] == "Summarize the current diff"


def test_formatters_tab_load_and_save(tk_root: tk.Tk) -> None:
    tab = FormattersTab(tk_root)
    source = {
        "formatter": {
            "python": {
                "disabled": False,
                "command": ["ruff", "format"],
                "extensions": [".py"],
                "environment": {"RUFF_CACHE_DIR": ".ruff_cache"},
            }
        }
    }
    tab.load_config(source)

    output: dict = {}
    tab.save_config(output)

    assert "formatter" in output
    assert output["formatter"]["python"]["command"] == ["ruff", "format"]
    assert output["formatter"]["python"]["environment"] == {"RUFF_CACHE_DIR": ".ruff_cache"}


def test_mcp_tab_load_and_save(tk_root: tk.Tk) -> None:
    tab = MCPServersTab(tk_root)
    source = {
        "mcp": {
            "filesystem": {
                "type": "local",
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                "enabled": True,
            },
            "remote-api": {
                "type": "remote",
                "url": "https://api.example.com/mcp",
                "enabled": True,
            },
        }
    }
    tab.load_config(source)

    output: dict = {}
    tab.save_config(output)

    assert "mcp" in output
    assert output["mcp"]["filesystem"]["type"] == "local"
    assert output["mcp"]["remote-api"]["type"] == "remote"


def test_lsp_tab_load_and_save(tk_root: tk.Tk) -> None:
    tab = LSPTab(tk_root)
    source = {
        "lsp": {
            "typescript": {
                "command": ["typescript-language-server", "--stdio"],
                "extensions": [".ts", ".tsx"],
                "disabled": False,
            }
        }
    }
    tab.load_config(source)

    output: dict = {}
    tab.save_config(output)

    assert "lsp" in output
    assert output["lsp"]["typescript"]["extensions"] == [".ts", ".tsx"]

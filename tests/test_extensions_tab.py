"""Tests for Extensions tab."""

from unittest.mock import MagicMock, patch

import pytest

from app.scanners import McpDescriptor, PluginDescriptor
from app.tabs.extensions import _CollapsibleSection


class TestCollapsibleSection:
    def test_toggle_expands_and_collapses(self) -> None:
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            section = _CollapsibleSection(root, "Test Section")
            section.pack()
            assert not section._expanded
            section._toggle()
            assert section._expanded
            section._toggle()
            assert not section._expanded
        finally:
            root.destroy()


class TestExtensionsTabLogic:
    def test_render_sections_empty_shows_empty_state(self) -> None:
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.extensions import ExtensionsTab
            tab = ExtensionsTab(root)
            tab._render_sections([], [])
            assert "No extensions found" in tab.status_label.cget("text")
        finally:
            root.destroy()

    def test_render_sections_with_plugins_and_mcp(self) -> None:
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.extensions import ExtensionsTab
            tab = ExtensionsTab(root)
            plugins = [
                PluginDescriptor(name="opencode-plugin-test", config_keys=["key1", "key2"])
            ]
            mcp_servers = [
                McpDescriptor(server_name="my-mcp", config_keys=["timeout"])
            ]
            tab._render_sections(plugins, mcp_servers)
            status = tab.status_label.cget("text")
            assert "2 extension" in status
        finally:
            root.destroy()

    def test_refresh_button_triggers_scan(self) -> None:
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.extensions import ExtensionsTab
            tab = ExtensionsTab(root)
            tab._loading = False
            with patch.object(tab, "_start_scan") as mock_scan:
                with patch.object(tab, "winfo_toplevel", return_value=MagicMock(opencode_data={})):
                    tab._refresh()
                    mock_scan.assert_called_once_with({})
        finally:
            root.destroy()

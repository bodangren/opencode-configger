"""Extensions tab for discovered plugins and MCP servers."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from app.scanners import (
    McpDescriptor,
    McpScanner,
    PluginDescriptor,
    PluginScanner,
)


class ExtensionsTab(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        on_change: Callable | None = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self._plugin_scanner = PluginScanner()
        self._mcp_scanner = McpScanner()
        self._loading = False

        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        ttk.Label(
            header, text="Extensions", font=("TkDefaultFont", 12, "bold")
        ).pack(side=tk.LEFT)
        self.refresh_btn = ttk.Button(
            header, text="Refresh Extensions", command=self._refresh
        )
        self.refresh_btn.pack(side=tk.RIGHT)
        self.status_label = ttk.Label(header, text="")
        self.status_label.pack(side=tk.RIGHT, padx=(0, 8))

        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_config(self, data: dict) -> None:
        self._start_scan(data)

    def save_config(self, data: dict) -> None:
        pass

    def _start_scan(self, config: dict) -> None:
        self._clear_sections()
        self._set_status("Scanning...", loading=True)
        self._loading = True
        self.after(50, lambda: self._run_scan(config))

    def _run_scan(self, config: dict) -> None:
        plugins = self._plugin_scanner.scan()
        mcp_servers = self._mcp_scanner.scan(config)
        self._loading = False
        self._render_sections(plugins, mcp_servers)

    def _refresh(self) -> None:
        if self._loading:
            return
        from app.main import App

        app = self.winfo_toplevel()
        if isinstance(app, App):
            self._start_scan(app.opencode_data or {})

    def _render_sections(
        self,
        plugins: list[PluginDescriptor],
        mcp_servers: list[McpDescriptor],
    ) -> None:
        self._clear_sections()
        total = len(plugins) + len(mcp_servers)
        if total == 0:
            self._set_status("No extensions found")
            self._show_empty_state()
            return
        self._set_status(f"Found {total} extension(s)")
        for plugin in plugins:
            self._add_plugin_section(plugin)
        for mcp in mcp_servers:
            self._add_mcp_section(mcp)

    def _clear_sections(self) -> None:
        for child in self.scroll_frame.winfo_children():
            child.destroy()

    def _show_empty_state(self) -> None:
        frame = ttk.Frame(self.scroll_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        ttk.Label(
            frame,
            text="No extensions found",
            font=("TkDefaultFont", 11),
            foreground="#888888",
        ).pack(pady=(20, 4))
        ttk.Label(
            frame,
            text="Install OpenCode plugins or configure MCP servers\n"
            "and click Refresh Extensions.",
            font=("TkDefaultFont", 9),
            foreground="#AAAAAA",
        ).pack()

    def _add_plugin_section(self, plugin: PluginDescriptor) -> None:
        section = _CollapsibleSection(self.scroll_frame, plugin.name)
        section.pack(fill=tk.X, padx=8, pady=(8, 4))
        self._add_descriptor_content(section.content, plugin.name, plugin.config_keys)

    def _add_mcp_section(self, mcp: McpDescriptor) -> None:
        section = _CollapsibleSection(self.scroll_frame, f"MCP: {mcp.server_name}")
        section.pack(fill=tk.X, padx=8, pady=(8, 4))
        self._add_descriptor_content(section.content, mcp.server_name, mcp.config_keys)

    def _add_descriptor_content(
        self, parent: ttk.Frame, name: str, config_keys: list[str]
    ) -> None:
        if config_keys:
            ttk.Label(
                parent, text=f"Config keys: {', '.join(config_keys)}", wraplength=400
            ).pack(anchor="w", pady=2)
        else:
            ttk.Label(
                parent,
                text="No machine-readable config keys found.\n"
                "This plugin/server does not advertise its configuration options.",
                wraplength=400,
                foreground="#888888",
                font=("TkDefaultFont", 9),
            ).pack(anchor="w", pady=2)

    def _set_status(self, text: str, loading: bool = False) -> None:
        self.status_label.config(text=text)
        self.refresh_btn.config(state="disabled" if loading else "normal")


class _CollapsibleSection(ttk.Frame):
    def __init__(self, parent: tk.Widget, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        self._expanded = False
        self.content = ttk.Frame(self, padding=(8, 4))

        self.header_btn = ttk.Label(
            self, text=f"+ {title}", font=("TkDefaultFont", 10, "bold"), cursor="plus"
        )
        self.header_btn.pack(anchor="w")
        self.header_btn.bind("<Button-1>", lambda _: self._toggle())

    def _toggle(self) -> None:
        if self._expanded:
            self.content.pack_forget()
            self.header_btn.config(text=f"+ {self.header_btn.cget('text')[2:]}")
        else:
            self.content.pack(fill=tk.X, pady=(4, 0))
            self.header_btn.config(text=f"- {self.header_btn.cget('text')[2:]}")
        self._expanded = not self._expanded
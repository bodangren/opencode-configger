"""MCP server configuration tab with local/remote type switcher."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from app.config_schema import MCP_LOCAL_FIELDS, MCP_REMOTE_FIELDS
from app.widgets import DynamicDictEditor, build_field_widget, _get_dotted, _set_dotted, _remove_dotted


class MCPServersTab(ttk.Frame):
    """Tab for dynamic MCP server entries under `mcp` key.

    Supports discriminated union: local (command-based) vs remote (URL-based).
    """

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.data: dict[str, dict] = {}

        ttk.Label(self, text="MCP Servers",
                  font=("TkDefaultFont", 12, "bold")).pack(
            anchor="w", padx=8, pady=(8, 12))

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Left panel: key list
        left = ttk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        ttk.Label(left, text="MCP Servers entries:").pack(anchor="w")
        self.key_listbox = tk.Listbox(left, width=25, height=12)
        self.key_listbox.pack(fill=tk.BOTH, expand=True, pady=(4, 4))
        self.key_listbox.bind("<<ListboxSelect>>", self._on_select)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X)
        self.new_key_var = tk.StringVar()
        ttk.Entry(btn_frame, textvariable=self.new_key_var, width=15).pack(
            side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Add", command=self._add_key, width=5).pack(
            side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Del", command=self._del_key, width=5).pack(
            side=tk.LEFT)

        # Right panel: type switcher + detail form
        right = ttk.LabelFrame(body, text="Details", padding=8)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        type_row = ttk.Frame(right)
        type_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(type_row, text="type", width=20, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))
        self.type_var = tk.StringVar(value="local")
        self.type_combo = ttk.Combobox(
            type_row, textvariable=self.type_var,
            values=["local", "remote"], state="readonly", width=15,
        )
        self.type_combo.pack(side=tk.LEFT)
        self.type_var.trace_add("write", lambda *_: self._on_type_changed())

        self.detail_frame = ttk.Frame(right)
        self.detail_frame.pack(fill=tk.BOTH, expand=True)

        self.local_widgets: dict[str, Any] = {}
        self.remote_widgets: dict[str, Any] = {}
        self._current_type = "local"

        self._build_type_form("local")

    def _build_type_form(self, mcp_type: str) -> None:
        for child in self.detail_frame.winfo_children():
            child.destroy()
        self.local_widgets.clear()
        self.remote_widgets.clear()

        fields = MCP_LOCAL_FIELDS if mcp_type == "local" else MCP_REMOTE_FIELDS
        widgets = self.local_widgets if mcp_type == "local" else self.remote_widgets

        for fd in fields:
            if fd.key == "type":
                continue  # handled by the type combo above
            w = build_field_widget(self.detail_frame, fd, on_change=self._save_current)
            w.pack(fill=tk.X, pady=2)
            widgets[fd.key] = w

        self._current_type = mcp_type

    def _on_type_changed(self) -> None:
        new_type = self.type_var.get()
        if new_type != self._current_type:
            self._save_current()
            self._build_type_form(new_type)
            # Load current entry data into new form
            sel = self.key_listbox.curselection()
            if sel:
                key = self.key_listbox.get(sel[0])
                self._load_entry(key)

    def _get_widgets(self) -> dict[str, Any]:
        return self.local_widgets if self._current_type == "local" else self.remote_widgets

    def _get_fields(self) -> list:
        return MCP_LOCAL_FIELDS if self._current_type == "local" else MCP_REMOTE_FIELDS

    def _on_select(self, event: tk.Event | None) -> None:
        sel = self.key_listbox.curselection()
        if not sel:
            return
        key = self.key_listbox.get(sel[0])
        entry_data = self.data.get(key, {})
        entry_type = entry_data.get("type", "local")
        if entry_type != self._current_type:
            self.type_var.set(entry_type)
        self._load_entry(key)

    def _load_entry(self, key: str) -> None:
        entry_data = self.data.get(key, {})
        widgets = self._get_widgets()
        fields = self._get_fields()
        for fd in fields:
            if fd.key == "type":
                continue
            if fd.key in widgets:
                val = _get_dotted(entry_data, fd.key)
                widgets[fd.key].set_value(val)

    def _save_current(self) -> None:
        sel = self.key_listbox.curselection()
        if not sel:
            return
        key = self.key_listbox.get(sel[0])
        entry_data = self.data.get(key, {})
        entry_data["type"] = self._current_type
        widgets = self._get_widgets()
        fields = self._get_fields()
        for fd in fields:
            if fd.key == "type":
                continue
            if fd.key in widgets:
                val = widgets[fd.key].get_value()
                if val is not None:
                    _set_dotted(entry_data, fd.key, val)
                else:
                    _remove_dotted(entry_data, fd.key)
        self.data[key] = entry_data
        if self.on_change:
            self.on_change()

    def _add_key(self) -> None:
        key = self.new_key_var.get().strip()
        if key and key not in self.data:
            self.data[key] = {"type": "local"}
            self.key_listbox.insert(tk.END, key)
            self.new_key_var.set("")
            if self.on_change:
                self.on_change()

    def _del_key(self) -> None:
        sel = self.key_listbox.curselection()
        if sel:
            key = self.key_listbox.get(sel[0])
            del self.data[key]
            self.key_listbox.delete(sel[0])
            for w in self._get_widgets().values():
                w.set_value(None)
            if self.on_change:
                self.on_change()

    def load_config(self, data: dict) -> None:
        mcp = data.get("mcp")
        self.data = dict(mcp) if isinstance(mcp, dict) else {}
        self.key_listbox.delete(0, tk.END)
        for key in self.data:
            self.key_listbox.insert(tk.END, key)

    def save_config(self, data: dict) -> None:
        if self.data:
            data["mcp"] = self.data
        else:
            data.pop("mcp", None)

"""Server settings tab."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from app.config_schema import SERVER_FIELDS, FieldType, get_nested, set_nested
from app.widgets import build_field_widget


class ServerTab(ttk.Frame):
    """Tab for server configuration."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.widgets: dict[str, Any] = {}

        ttk.Label(self, text="Server Settings",
                  font=("TkDefaultFont", 12, "bold")).pack(
            anchor="w", padx=8, pady=(8, 12))

        form = ttk.Frame(self)
        form.pack(fill=tk.BOTH, expand=True, padx=8)

        for fd in SERVER_FIELDS:
            w = build_field_widget(form, fd, on_change=on_change)
            w.pack(fill=tk.X, pady=3)
            self.widgets[fd.key] = w

    def load_config(self, data: dict) -> None:
        for fd in SERVER_FIELDS:
            val = get_nested(data, fd.full_key)
            self.widgets[fd.key].set_value(val)

    def save_config(self, data: dict) -> None:
        has_values = False
        for fd in SERVER_FIELDS:
            val = self.widgets[fd.key].get_value()
            if val is not None:
                has_values = True
                if fd.field_type == FieldType.INTEGER:
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        continue
                set_nested(data, fd.full_key, val)
        if not has_values:
            data.pop("server", None)

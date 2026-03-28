"""Tools and permission settings tab."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.config_schema import PERMISSION_TOOLS
from app.widgets import PermissionRow


class ToolsTab(ttk.Frame):
    """Tab for per-tool permission values under `permission` key."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.rows: dict[str, PermissionRow] = {}

        ttk.Label(self, text="Tool Permissions",
                  font=("TkDefaultFont", 12, "bold")).pack(
            anchor="w", padx=8, pady=(8, 12))

        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)

        inner.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8), padx=(0, 8))

        for tool in PERMISSION_TOOLS:
            row = PermissionRow(inner, tool, on_change=on_change)
            row.pack(fill=tk.X, pady=2)
            self.rows[tool] = row

    def load_config(self, data: dict) -> None:
        """Load permission values from config."""
        permission = data.get("permission", {})
        for tool, row in self.rows.items():
            row.set_value(permission.get(tool))

    def save_config(self, data: dict) -> None:
        """Save permission values into config."""
        permission: dict[str, str] = {}
        for tool, row in self.rows.items():
            value = row.get_value()
            if value:
                permission[tool] = value

        if permission:
            data["permission"] = permission
        else:
            data.pop("permission", None)

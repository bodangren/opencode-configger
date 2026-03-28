"""LSP server configuration tab."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.config_schema import LSP_ENTRY_FIELDS
from app.widgets import DynamicDictEditor


class LSPTab(ttk.Frame):
    """Tab for dynamic LSP server entries under `lsp` key."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change

        ttk.Label(self, text="LSP Servers",
                  font=("TkDefaultFont", 12, "bold")).pack(
            anchor="w", padx=8, pady=(8, 12))

        self.editor = DynamicDictEditor(
            self,
            section_name="LSP Servers",
            entry_fields=LSP_ENTRY_FIELDS,
            on_change=on_change,
        )
        self.editor.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def load_config(self, data: dict) -> None:
        lsp = data.get("lsp")
        if lsp is False:
            self.editor.set_value({})
        else:
            self.editor.set_value(lsp)

    def save_config(self, data: dict) -> None:
        value = self.editor.get_value()
        if value:
            data["lsp"] = value
        else:
            data.pop("lsp", None)

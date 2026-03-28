"""Formatter configuration tab."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.config_schema import FORMATTER_ENTRY_FIELDS
from app.widgets import DynamicDictEditor


class FormattersTab(ttk.Frame):
    """Tab for dynamic formatter entries under `formatter` key."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change

        ttk.Label(self, text="Formatter Configuration",
                  font=("TkDefaultFont", 12, "bold")).pack(
            anchor="w", padx=8, pady=(8, 12))

        self.editor = DynamicDictEditor(
            self,
            section_name="Formatters",
            entry_fields=FORMATTER_ENTRY_FIELDS,
            on_change=on_change,
        )
        self.editor.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def load_config(self, data: dict) -> None:
        """Load formatter data from config."""
        self.editor.set_value(data.get("formatter"))

    def save_config(self, data: dict) -> None:
        """Save formatter data into config."""
        value = self.editor.get_value()
        if value:
            data["formatter"] = value
        else:
            data.pop("formatter", None)

"""General settings tab for opencode.json top-level fields."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from app.config_schema import GENERAL_FIELDS, FieldType, get_nested, set_nested
from app.widgets import build_field_widget


class GeneralTab(ttk.Frame):
    """Tab for general OpenCode settings."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 on_pick_model_request: Callable[[str], None] | None = None,
                 on_validate_field: Callable[[str, str | None], None] | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.on_pick_model_request = on_pick_model_request
        self.on_validate_field = on_validate_field
        self.widgets: dict[str, Any] = {}

        ttk.Label(self, text="General Settings",
                  font=("TkDefaultFont", 12, "bold")).pack(
            anchor="w", padx=8, pady=(8, 12))

        form = ttk.Frame(self)
        form.pack(fill=tk.BOTH, expand=True, padx=8)

        for fd in GENERAL_FIELDS:
            w = build_field_widget(form, fd, on_change=self._handle_change)
            w.pack(fill=tk.X, pady=3)
            self.widgets[fd.key] = w

        chooser_row = ttk.Frame(self)
        chooser_row.pack(fill=tk.X, padx=8, pady=(8, 4))
        ttk.Button(
            chooser_row,
            text="Choose model from browser...",
            command=lambda: self._request_model_pick("model"),
        ).pack(side=tk.LEFT)
        ttk.Button(
            chooser_row,
            text="Choose small_model from browser...",
            command=lambda: self._request_model_pick("small_model"),
        ).pack(side=tk.LEFT, padx=(8, 0))

    def _request_model_pick(self, target: str) -> None:
        if self.on_pick_model_request:
            self.on_pick_model_request(target)

    def _handle_change(self) -> None:
        if self.on_change:
            self.on_change()

    def load_config(self, data: dict) -> None:
        """Load config values into the form widgets."""
        for fd in GENERAL_FIELDS:
            val = get_nested(data, fd.full_key)
            self.widgets[fd.key].set_value(val)

    def save_config(self, data: dict) -> None:
        """Save form widget values back into the config dict."""
        for fd in GENERAL_FIELDS:
            val = self.widgets[fd.key].get_value()
            if val is not None:
                # Type coercion
                if fd.field_type == FieldType.BOOLEAN:
                    pass  # already bool
                elif fd.field_type == FieldType.INTEGER:
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        continue
                elif fd.key == "autoupdate":
                    # Special: can be bool or "notify"
                    if val == "true":
                        val = True
                    elif val == "false":
                        val = False
                    elif val != "notify":
                        continue
                set_nested(data, fd.full_key, val)

    def set_field_value(self, key: str, value: Any) -> None:
        """Set one field widget value by key.

        Args:
            key: Field key in GENERAL_FIELDS.
            value: Value to set.
        """
        if key in self.widgets:
            self.widgets[key].set_value(value)
            self._handle_change()

"""Compaction, watcher, instructions, plugins, skills, provider list,
experimental, and enterprise tab."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from app.config_schema import (
    COMPACTION_FIELDS, WATCHER_FIELDS, INSTRUCTIONS_FIELDS,
    PLUGIN_FIELDS, SKILLS_FIELDS, PROVIDER_LIST_FIELDS,
    EXPERIMENTAL_FIELDS, ENTERPRISE_FIELDS,
    FieldType, get_nested, set_nested,
)
from app.widgets import SectionFrame, build_field_widget


class AdvancedTab(ttk.Frame):
    """Tab for compaction, watcher, instructions, plugins, skills,
    provider lists, experimental, and enterprise settings."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.widgets: dict[str, Any] = {}

        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._add_section("Compaction", COMPACTION_FIELDS)
        self._add_section("Watcher", WATCHER_FIELDS)
        self._add_section("Instructions", INSTRUCTIONS_FIELDS)
        self._add_section("Plugins", PLUGIN_FIELDS)
        self._add_section("Skills", SKILLS_FIELDS)
        self._add_section("Provider Lists", PROVIDER_LIST_FIELDS)
        self._add_section("Experimental", EXPERIMENTAL_FIELDS, collapsed=True)
        self._add_section("Enterprise", ENTERPRISE_FIELDS, collapsed=True)

    def _add_section(self, title: str, fields: list,
                     collapsed: bool = False) -> None:
        sf = SectionFrame(self.scroll_frame, text=title, collapsed=collapsed)
        sf.pack(fill=tk.X, padx=8, pady=(8, 4))

        for fd in fields:
            w = build_field_widget(sf.content, fd, on_change=self.on_change)
            w.pack(fill=tk.X, pady=2)
            self.widgets[fd.full_key] = w

    @property
    def _all_fields(self) -> list:
        return (COMPACTION_FIELDS + WATCHER_FIELDS +
                INSTRUCTIONS_FIELDS + PLUGIN_FIELDS +
                SKILLS_FIELDS + PROVIDER_LIST_FIELDS +
                EXPERIMENTAL_FIELDS + ENTERPRISE_FIELDS)

    def load_config(self, data: dict) -> None:
        for fd in self._all_fields:
            key = fd.full_key
            if key in self.widgets:
                val = get_nested(data, key)
                self.widgets[key].set_value(val)

    def save_config(self, data: dict) -> None:
        for fd in self._all_fields:
            key = fd.full_key
            if key in self.widgets:
                val = self.widgets[key].get_value()
                if val is not None:
                    if fd.field_type == FieldType.INTEGER:
                        try:
                            val = int(val)
                        except (ValueError, TypeError):
                            continue
                    set_nested(data, key, val)

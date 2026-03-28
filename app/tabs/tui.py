"""TUI configuration tab with keybinding editor."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable

from app.config_io import load_jsonc, new_tui_config, save_json
from app.config_schema import (
    KEYBIND_DEFAULTS,
    KEYBIND_SLOTS,
    TUI_FIELDS,
    TUI_SCROLL_ACCEL_FIELDS,
    FieldType,
    get_nested,
    set_nested,
)
from app.dialogs.file_picker import choose_open_config, choose_save_config
from app.widgets import build_field_widget


class KeybindEditor(ttk.LabelFrame):
    """Searchable editor for all known keybinding slots."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, text="Keybindings", padding=8, **kwargs)
        self.on_change = on_change
        self._updating = False
        self._values: dict[str, str] = {}
        self._filtered: list[str] = list(KEYBIND_SLOTS)

        search_row = ttk.Frame(self)
        search_row.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(search_row, text="Search:").pack(side=tk.LEFT, padx=(0, 6))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_var.trace_add("write", lambda *_: self._refresh_list())

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.Frame(body)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.slot_list = tk.Listbox(list_frame, height=12)
        self.slot_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        slot_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                                    command=self.slot_list.yview)
        slot_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.slot_list.configure(yscrollcommand=slot_scroll.set)
        self.slot_list.bind("<<ListboxSelect>>", self._on_slot_selected)

        value_frame = ttk.LabelFrame(body, text="Binding", padding=8)
        value_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(value_frame, text="Selected slot:").pack(anchor="w")
        self.slot_label = ttk.Label(value_frame, text="(none)")
        self.slot_label.pack(anchor="w", pady=(0, 6))
        ttk.Label(value_frame, text="Key sequence:").pack(anchor="w")
        self.value_var = tk.StringVar()
        value_entry = ttk.Entry(value_frame, textvariable=self.value_var)
        value_entry.pack(fill=tk.X, pady=(0, 6))
        self.value_var.trace_add("write", lambda *_: self._on_value_changed())
        self.default_label = ttk.Label(
            value_frame,
            text="Default: (none)",
        )
        self.default_label.pack(anchor="w")

        self._refresh_list()

    def _refresh_list(self) -> None:
        query = self.search_var.get().strip().lower()
        selected_before = self._selected_slot()
        if query:
            self._filtered = [slot for slot in KEYBIND_SLOTS if query in slot.lower()]
        else:
            self._filtered = list(KEYBIND_SLOTS)

        self.slot_list.delete(0, tk.END)
        for slot in self._filtered:
            self.slot_list.insert(tk.END, slot)

        if selected_before and selected_before in self._filtered:
            index = self._filtered.index(selected_before)
            self.slot_list.selection_set(index)
            self.slot_list.activate(index)
        elif self._filtered:
            self.slot_list.selection_set(0)
            self.slot_list.activate(0)
        self._on_slot_selected(None)

    def _selected_slot(self) -> str | None:
        selection = self.slot_list.curselection()
        if not selection:
            return None
        idx = selection[0]
        if idx < 0 or idx >= len(self._filtered):
            return None
        return self._filtered[idx]

    def _on_slot_selected(self, _event: tk.Event | None) -> None:
        slot = self._selected_slot()
        self._updating = True
        if slot is None:
            self.slot_label.config(text="(none)")
            self.value_var.set("")
            self.default_label.config(text="Default: (none)")
        else:
            self.slot_label.config(text=slot)
            self.value_var.set(self._values.get(slot, ""))
            default = KEYBIND_DEFAULTS.get(slot, "none")
            self.default_label.config(text=f"Default: {default}")
        self._updating = False

    def _on_value_changed(self) -> None:
        if self._updating:
            return

        slot = self._selected_slot()
        if slot is None:
            return

        value = self.value_var.get().strip()
        if value:
            self._values[slot] = value
        else:
            self._values.pop(slot, None)

        if self.on_change:
            self.on_change()

    def set_value(self, value: Any) -> None:
        """Load keybinding overrides into the editor."""
        self._values = {}
        if isinstance(value, dict):
            for key, val in value.items():
                if key in KEYBIND_SLOTS and isinstance(val, str):
                    self._values[key] = val
        self._refresh_list()

    def get_value(self) -> dict[str, str] | None:
        """Return keybinding overrides, or None when empty."""
        return dict(self._values) if self._values else None


class TuiTab(ttk.Frame):
    """Tab for tui.json settings and keybindings."""

    def __init__(self, parent: tk.Widget, on_change: Callable | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.current_path: Path | None = None
        self.widgets: dict[str, Any] = {}
        self.data: dict[str, Any] = new_tui_config()

        top_row = ttk.Frame(self)
        top_row.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Label(top_row, text="TUI Settings",
                  font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(top_row, text="Load TUI...",
                   command=self.load_tui_file).pack(side=tk.RIGHT)
        ttk.Button(top_row, text="Save TUI As...",
                   command=self.save_tui_file_as).pack(side=tk.RIGHT, padx=(0, 6))
        ttk.Button(top_row, text="Save TUI",
                   command=self.save_tui_file).pack(side=tk.RIGHT, padx=(0, 6))

        self.path_var = tk.StringVar(value="Path: (new tui.json)")
        ttk.Label(self, textvariable=self.path_var).pack(
            anchor="w", padx=8, pady=(0, 8)
        )

        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        settings_frame = ttk.LabelFrame(content, text="Core Settings", padding=8)
        settings_frame.pack(fill=tk.X, pady=(0, 8))

        all_fields = TUI_FIELDS + TUI_SCROLL_ACCEL_FIELDS
        for field_def in all_fields:
            widget = build_field_widget(settings_frame, field_def,
                                        on_change=on_change)
            widget.pack(fill=tk.X, pady=2)
            self.widgets[field_def.full_key] = widget

        self.keybind_editor = KeybindEditor(content, on_change=on_change)
        self.keybind_editor.pack(fill=tk.BOTH, expand=True)

    def _refresh_path_label(self) -> None:
        if self.current_path:
            self.path_var.set(f"Path: {self.current_path}")
        else:
            self.path_var.set("Path: (new tui.json)")

    def load_config(self, data: dict[str, Any]) -> None:
        """Load provided tui data into widgets."""
        self.data = dict(data)
        all_fields = TUI_FIELDS + TUI_SCROLL_ACCEL_FIELDS
        for field_def in all_fields:
            value = get_nested(self.data, field_def.full_key)
            self.widgets[field_def.full_key].set_value(value)
        self.keybind_editor.set_value(self.data.get("keybinds"))

    def save_config(self, data: dict[str, Any]) -> None:
        """Save widget values into provided tui dictionary."""
        data.clear()
        data["$schema"] = self.data.get("$schema", "https://opencode.ai/tui.json")

        all_fields = TUI_FIELDS + TUI_SCROLL_ACCEL_FIELDS
        for field_def in all_fields:
            value = self.widgets[field_def.full_key].get_value()
            if value is None:
                continue
            if field_def.field_type == FieldType.NUMBER:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue
            set_nested(data, field_def.full_key, value)

        keybinds = self.keybind_editor.get_value()
        if keybinds:
            data["keybinds"] = keybinds

    def load_tui_file(self) -> None:
        """Open dialog and load selected tui.json file."""
        selected = choose_open_config(
            initial_dir=self.current_path.parent if self.current_path else None,
        )
        if not selected:
            return
        try:
            loaded = load_jsonc(selected)
        except Exception as exc:
            messagebox.showerror("Load TUI failed", f"Could not load file:\n{exc}")
            return
        if not isinstance(loaded, dict):
            messagebox.showerror("Load TUI failed", "TUI config must be a JSON object")
            return

        self.current_path = selected
        self.load_config(loaded)
        self._refresh_path_label()

    def save_tui_file(self) -> bool:
        """Save current tui config to disk.

        Returns:
            True if save succeeds.
        """
        if self.current_path is None:
            return self.save_tui_file_as()

        output: dict[str, Any] = {}
        self.save_config(output)
        try:
            save_json(self.current_path, output)
        except Exception as exc:
            messagebox.showerror("Save TUI failed", f"Could not save file:\n{exc}")
            return False
        self.data = output
        return True

    def save_tui_file_as(self) -> bool:
        """Save current tui config to a user-selected path.

        Returns:
            True if save succeeds.
        """
        selected = choose_save_config(
            initial_path=self.current_path,
            default_filename="tui.json",
        )
        if not selected:
            return False
        self.current_path = selected
        self._refresh_path_label()
        return self.save_tui_file()

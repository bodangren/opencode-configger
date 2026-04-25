"""Reusable form widgets for the OpenCode Configger GUI."""

import json
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from app.config_schema import FieldDef, FieldType


class ToolTip:
    """Simple tooltip that appears on hover."""

    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event: tk.Event) -> None:
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#0D0D0D", foreground="#F2F2F2",
            relief=tk.SOLID, borderwidth=1,
            font=("TkDefaultFont", 9),
            wraplength=400, padx=6, pady=4,
        )
        label.pack()

    def _hide(self, event: tk.Event) -> None:
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

    def set_text(self, text: str) -> None:
        self.text = text
        if self.tip_window:
            label = self.tip_window.winfo_children()[0]
            label.config(text=text)

    def show(self) -> None:
        self._show(None)


class LabeledEntry(ttk.Frame):
    """A labeled text entry with optional tooltip and placeholder."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        self.label = ttk.Label(self, text=field_def.key, width=20, anchor="w")
        self.label.pack(side=tk.LEFT, padx=(0, 8))

        self._entry_frame = tk.Frame(self, highlightbackground="#FF2D55", highlightthickness=0)
        self._entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry_frame.pack_propagate(False)

        self.var = tk.StringVar()
        self.entry = ttk.Entry(self._entry_frame, textvariable=self.var, width=40)
        self.entry.pack(fill=tk.X, expand=True)

        if field_def.default is not None:
            self.entry.config(
                foreground="#555555"
            )
            self.var.set("")

        if on_change:
            self.var.trace_add("write", lambda *_: on_change())

        ToolTip(self.entry, field_def.description)
        if field_def.default is not None:
            ToolTip(self.label, f"{field_def.description}\nDefault: {field_def.default}")
        else:
            ToolTip(self.label, field_def.description)

        self._error_tooltip: ToolTip | None = None

    def show_error(self, message: str) -> None:
        self._entry_frame.config(highlightthickness=2)
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip.set_text(message)
            self._error_tooltip.show()
        else:
            self._error_tooltip = ToolTip(self.entry, message)

    def clear_error(self) -> None:
        self._entry_frame.config(highlightthickness=0)
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip = None

    def get_value(self) -> str | None:
        val = self.var.get().strip()
        return val if val else None

    def set_value(self, value: Any) -> None:
        self.var.set(str(value) if value is not None else "")


class LabeledCombo(ttk.Frame):
    """A labeled dropdown/combobox for enum fields."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        self.label = ttk.Label(self, text=field_def.key, width=20, anchor="w")
        self.label.pack(side=tk.LEFT, padx=(0, 8))

        self._combo_frame = tk.Frame(self, highlightbackground="#FF2D55", highlightthickness=0)
        self._combo_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._combo_frame.pack_propagate(False)

        values = [""] + field_def.enum_values
        self.var = tk.StringVar()
        self.combo = ttk.Combobox(
            self._combo_frame, textvariable=self.var, values=values,
            state="readonly", width=37,
        )
        self.combo.pack(fill=tk.X, expand=True)

        if on_change:
            self.combo.bind("<<ComboboxSelected>>", lambda _: on_change())

        ToolTip(self.combo, field_def.description)
        ToolTip(self.label, field_def.description)

        self._error_tooltip: ToolTip | None = None

    def show_error(self, message: str) -> None:
        self._combo_frame.config(highlightthickness=2)
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip.set_text(message)
            self._error_tooltip.show()
        else:
            self._error_tooltip = ToolTip(self.combo, message)

    def clear_error(self) -> None:
        self._combo_frame.config(highlightthickness=0)
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip = None

    def get_value(self) -> str | None:
        val = self.var.get()
        return val if val else None

    def set_value(self, value: Any) -> None:
        self.var.set(str(value) if value is not None else "")


class LabeledSuggest(ttk.Frame):
    """A labeled editable combobox with suggested values."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def

        self.label = ttk.Label(self, text=field_def.key, width=20, anchor="w")
        self.label.pack(side=tk.LEFT, padx=(0, 8))

        self.var = tk.StringVar()
        self.combo = ttk.Combobox(
            self,
            textvariable=self.var,
            values=field_def.suggestions,
            state="normal",
            width=37,
        )
        self.combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if on_change:
            self.combo.bind("<<ComboboxSelected>>", lambda _e: on_change())
            self.var.trace_add("write", lambda *_: on_change())

        ToolTip(self.combo, field_def.description)
        ToolTip(self.label, field_def.description)

    def get_value(self) -> str | None:
        value = self.var.get().strip()
        return value if value else None

    def set_value(self, value: Any) -> None:
        self.var.set(str(value) if value is not None else "")


class LabeledStringOrBool(ttk.Frame):
    """A labeled selector for string-or-boolean fields."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def

        self.label = ttk.Label(self, text=field_def.key, width=20, anchor="w")
        self.label.pack(side=tk.LEFT, padx=(0, 8))

        self.var = tk.StringVar()
        self.combo = ttk.Combobox(
            self,
            textvariable=self.var,
            values=["", "true", "false", "notify"],
            state="readonly",
            width=37,
        )
        self.combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if on_change:
            self.combo.bind("<<ComboboxSelected>>", lambda _e: on_change())

        ToolTip(self.combo, field_def.description)
        ToolTip(self.label, field_def.description)

    def get_value(self) -> str | None:
        value = self.var.get()
        return value if value else None

    def set_value(self, value: Any) -> None:
        if isinstance(value, bool):
            self.var.set("true" if value else "false")
            return
        self.var.set(str(value) if value is not None else "")


class LabeledCheck(ttk.Frame):
    """A labeled checkbox for boolean fields."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        self.var = tk.BooleanVar(value=False)
        self.check = ttk.Checkbutton(
            self, text=field_def.key, variable=self.var,
        )
        self.check.pack(side=tk.LEFT)

        self._error_tooltip: ToolTip | None = None

        # Track whether the value has been explicitly set vs left as default
        self.is_set = False

        if on_change:
            self.var.trace_add("write", lambda *_: self._on_toggle())

        ToolTip(self.check, field_def.description)

    def _on_toggle(self) -> None:
        self.is_set = True
        if self.on_change:
            self.on_change()

    def show_error(self, message: str) -> None:
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip.set_text(message)
            self._error_tooltip.show()
        else:
            self._error_tooltip = ToolTip(self.check, message)

    def clear_error(self) -> None:
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip = None

    def get_value(self) -> bool | None:
        if not self.is_set:
            return None
        return self.var.get()

    def set_value(self, value: Any) -> None:
        if value is not None:
            self.var.set(bool(value))
            self.is_set = True
        else:
            self.var.set(bool(self.field_def.default) if self.field_def.default is not None else False)
            self.is_set = False


class StringListEditor(ttk.Frame):
    """Editor for a list of strings (e.g., CORS origins, ignore patterns)."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        header = ttk.Frame(self)
        header.pack(fill=tk.X)

        ttk.Label(header, text=field_def.key, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))

        self.add_var = tk.StringVar()
        self.add_entry = ttk.Entry(header, textvariable=self.add_var, width=30)
        self.add_entry.pack(side=tk.LEFT, padx=(0, 4))
        self.add_entry.bind("<Return>", lambda _: self._add_item())

        ttk.Button(header, text="Add", command=self._add_item, width=5).pack(
            side=tk.LEFT, padx=(0, 4))
        ttk.Button(header, text="Remove", command=self._remove_item, width=7).pack(
            side=tk.LEFT)

        self.listbox = tk.Listbox(self, height=4, width=60)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        ToolTip(self.add_entry, field_def.description)

    def _add_item(self) -> None:
        val = self.add_var.get().strip()
        if val:
            self.listbox.insert(tk.END, val)
            self.add_var.set("")
            if self.on_change:
                self.on_change()

    def _remove_item(self) -> None:
        sel = self.listbox.curselection()
        if sel:
            self.listbox.delete(sel[0])
            if self.on_change:
                self.on_change()

    def get_value(self) -> list[str] | None:
        items = list(self.listbox.get(0, tk.END))
        return items if items else None

    def set_value(self, value: Any) -> None:
        self.listbox.delete(0, tk.END)
        if isinstance(value, list):
            for item in value:
                self.listbox.insert(tk.END, str(item))


class PermissionRow(ttk.Frame):
    """A row for a single tool permission (allow/ask/deny)."""

    def __init__(self, parent: tk.Widget, tool_name: str,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.tool_name = tool_name
        self.on_change = on_change

        ttk.Label(self, text=tool_name, width=20, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))

        self.var = tk.StringVar(value="")
        combo = ttk.Combobox(
            self, textvariable=self.var,
            values=["", "allow", "ask", "deny"],
            state="readonly", width=10,
        )
        combo.pack(side=tk.LEFT)

        if on_change:
            combo.bind("<<ComboboxSelected>>", lambda _: on_change())

        ToolTip(combo, f"Permission level for the '{tool_name}' tool")

    def get_value(self) -> str | None:
        val = self.var.get()
        return val if val else None

    def set_value(self, value: Any) -> None:
        self.var.set(str(value) if value else "")


class ObjectEditor(ttk.Frame):
    """Editor for JSON object values."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def

        self.label = ttk.Label(self, text=field_def.key, width=20, anchor="w")
        self.label.pack(side=tk.LEFT, padx=(0, 8))

        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var, width=40)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if on_change:
            self.var.trace_add("write", lambda *_: on_change())

        ToolTip(self.entry, f"{field_def.description} (JSON object)")
        ToolTip(self.label, field_def.description)

    def get_value(self) -> dict[str, Any] | None:
        val = self.var.get().strip()
        if not val:
            return None
        try:
            parsed = json.loads(val)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict):
            return parsed
        return None

    def set_value(self, value: Any) -> None:
        if isinstance(value, dict):
            self.var.set(json.dumps(value))
        else:
            self.var.set("")


class SectionFrame(ttk.LabelFrame):
    """Collapsible LabelFrame that can expand/collapse with a toggle button."""

    def __init__(self, parent: tk.Widget, text: str = "",
                 collapsed: bool = False, **kwargs):
        super().__init__(parent, text=f"  {text}", **kwargs)
        self.section_text = text
        self._collapsed = collapsed

        self.toggle_btn = ttk.Button(
            self, text="−", width=2, command=self.toggle,
        )
        self.toggle_btn.place(relx=0.0, rely=0.0, x=4, y=-2)

        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        if collapsed:
            self.content.pack_forget()
            self.toggle_btn.config(text="+")

    def toggle(self) -> None:
        if self._collapsed:
            self.content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            self.toggle_btn.config(text="−")
            self._collapsed = False
        else:
            self.content.pack_forget()
            self.toggle_btn.config(text="+")
            self._collapsed = True

    @property
    def collapsed(self) -> bool:
        return self._collapsed


class RadioGroup(ttk.Frame):
    """Horizontal or vertical radio buttons for small enums (≤5 values)."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        ttk.Label(self, text=field_def.key, width=20, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))

        self.var = tk.StringVar(value="")
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.LEFT)

        for val in field_def.enum_values:
            rb = ttk.Radiobutton(btn_frame, text=val, value=val,
                                 variable=self.var)
            rb.pack(side=tk.LEFT, padx=(0, 6))

        if on_change:
            self.var.trace_add("write", lambda *_: on_change())

        ToolTip(btn_frame, field_def.description)

    def get_value(self) -> str | None:
        val = self.var.get()
        return val if val else None

    def set_value(self, value: Any) -> None:
        self.var.set(str(value) if value is not None else "")


class LabeledSpinbox(ttk.Frame):
    """Integer/float spinbox with min/max/step, label, tooltip."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change
        self.is_set = False

        ttk.Label(self, text=field_def.key, width=20, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))

        self._spinbox_frame = tk.Frame(self, highlightbackground="#FF2D55", highlightthickness=0)
        self._spinbox_frame.pack(side=tk.LEFT)
        self._spinbox_frame.pack_propagate(False)

        from_val = int(field_def.min_value) if field_def.min_value is not None else 0
        to_val = int(field_def.max_value) if field_def.max_value is not None else 999999

        self.var = tk.StringVar(value="")
        self.spinbox = ttk.Spinbox(
            self._spinbox_frame, textvariable=self.var,
            from_=from_val, to=to_val, width=15,
        )
        self.spinbox.pack()

        if on_change:
            self.var.trace_add("write", lambda *_: self._on_edit())

        ToolTip(self.spinbox, field_def.description)

        self._error_tooltip: ToolTip | None = None

    def _on_edit(self) -> None:
        self.is_set = True
        if self.on_change:
            self.on_change()

    def show_error(self, message: str) -> None:
        self._spinbox_frame.config(highlightthickness=2)
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip.set_text(message)
            self._error_tooltip.show()
        else:
            self._error_tooltip = ToolTip(self.spinbox, message)

    def clear_error(self) -> None:
        self._spinbox_frame.config(highlightthickness=0)
        if self._error_tooltip:
            self._error_tooltip._hide(None)
            self._error_tooltip = None

    def get_value(self) -> int | None:
        if not self.is_set:
            return None
        val = self.var.get().strip()
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def set_value(self, value: Any) -> None:
        if value is not None:
            self.var.set(str(int(value)))
            self.is_set = True
        else:
            self.var.set("")
            self.is_set = False


class LabeledSlider(ttk.Frame):
    """Slider + entry for 0–1 range values (temperature, top_p)."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change
        self.is_set = False

        ttk.Label(self, text=field_def.key, width=20, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))

        from_val = field_def.min_value if field_def.min_value is not None else 0.0
        to_val = field_def.max_value if field_def.max_value is not None else 1.0

        self.var = tk.DoubleVar(value=from_val)
        self.scale = ttk.Scale(
            self, variable=self.var, from_=from_val, to=to_val,
            orient=tk.HORIZONTAL, length=200,
        )
        self.scale.pack(side=tk.LEFT, padx=(0, 8))

        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.entry_var, width=8)
        self.entry.pack(side=tk.LEFT)

        self.var.trace_add("write", lambda *_: self._sync_entry())
        self.entry_var.trace_add("write", lambda *_: self._sync_slider())

        ToolTip(self.scale, field_def.description)

    def _sync_entry(self) -> None:
        val = self.var.get()
        self.entry_var.set(f"{val:.2f}")
        self.is_set = True
        if self.on_change:
            self.on_change()

    def _sync_slider(self) -> None:
        try:
            val = float(self.entry_var.get())
            self.var.set(val)
            self.is_set = True
        except ValueError:
            pass

    def get_value(self) -> float | None:
        if not self.is_set:
            return None
        return round(self.var.get(), 2)

    def set_value(self, value: Any) -> None:
        if value is not None:
            self.var.set(float(value))
            self.is_set = True
        else:
            self.var.set(self.field_def.min_value or 0.0)
            self.is_set = False


class ColorPicker(ttk.Frame):
    """Color picker with hex entry + theme-color dropdown."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        ttk.Label(self, text=field_def.key, width=20, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))

        self.var = tk.StringVar(value="")
        values = [""] + (field_def.enum_values or [])
        self.combo = ttk.Combobox(
            self, textvariable=self.var, values=values,
            width=15,
        )
        self.combo.pack(side=tk.LEFT, padx=(0, 4))

        self.swatch = tk.Label(self, width=3, bg="#333333", relief=tk.SUNKEN)
        self.swatch.pack(side=tk.LEFT, padx=(0, 4))

        ttk.Button(self, text="Pick…", command=self._pick_color, width=6).pack(
            side=tk.LEFT)

        if on_change:
            self.var.trace_add("write", lambda *_: on_change())
        self.var.trace_add("write", lambda *_: self._update_swatch())

        ToolTip(self.combo, field_def.description)

    def _pick_color(self) -> None:
        from tkinter import colorchooser
        color = colorchooser.askcolor(title=f"Choose {self.field_def.key}")[1]
        if color:
            self.var.set(color)

    def _update_swatch(self) -> None:
        val = self.var.get()
        if val.startswith("#") and len(val) in (4, 7):
            try:
                self.swatch.config(bg=val)
            except tk.TclError:
                pass

    def get_value(self) -> str | None:
        val = self.var.get().strip()
        return val if val else None

    def set_value(self, value: Any) -> None:
        self.var.set(str(value) if value is not None else "")


class KeyValueEditor(ttk.Frame):
    """Two-column table (key, value) with add/remove for Record<string,string>."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        ttk.Label(self, text=field_def.key, anchor="w").pack(anchor="w")

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.tree = ttk.Treeview(
            tree_frame, columns=("key", "value"), show="headings", height=4,
        )
        self.tree.heading("key", text="Key")
        self.tree.heading("value", text="Value")
        self.tree.column("key", width=150)
        self.tree.column("value", width=200)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=sb.set)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(4, 0))

        self.key_var = tk.StringVar()
        self.val_var = tk.StringVar()
        ttk.Entry(btn_frame, textvariable=self.key_var, width=15).pack(
            side=tk.LEFT, padx=(0, 4))
        ttk.Entry(btn_frame, textvariable=self.val_var, width=20).pack(
            side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Add", command=self._add_row, width=5).pack(
            side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Remove", command=self._remove_row, width=7).pack(
            side=tk.LEFT)

        ToolTip(self.tree, field_def.description)

    def _add_row(self) -> None:
        k = self.key_var.get().strip()
        v = self.val_var.get().strip()
        if k:
            self.tree.insert("", tk.END, values=(k, v))
            self.key_var.set("")
            self.val_var.set("")
            if self.on_change:
                self.on_change()

    def _remove_row(self) -> None:
        sel = self.tree.selection()
        if sel:
            self.tree.delete(sel[0])
            if self.on_change:
                self.on_change()

    def get_value(self) -> dict[str, str] | None:
        items = {}
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            items[vals[0]] = vals[1]
        return items if items else None

    def set_value(self, value: Any) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        if isinstance(value, dict):
            for k, v in value.items():
                self.tree.insert("", tk.END, values=(str(k), str(v)))


class MultilineText(ttk.Frame):
    """Labeled scrolled text widget for prompt and template fields."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change

        ttk.Label(self, text=field_def.key, anchor="w").pack(anchor="w")

        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.text = tk.Text(text_frame, height=5, width=50, wrap=tk.WORD)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=sb.set)

        if on_change:
            self.text.bind("<<Modified>>", lambda _: self._on_modified())

        ToolTip(self.text, field_def.description)

    def _on_modified(self) -> None:
        if self.text.edit_modified():
            if self.on_change:
                self.on_change()
            self.text.edit_modified(False)

    def get_value(self) -> str | None:
        val = self.text.get("1.0", tk.END).rstrip("\n")
        return val if val else None

    def set_value(self, value: Any) -> None:
        self.text.delete("1.0", tk.END)
        if value is not None:
            self.text.insert("1.0", str(value))


class SearchableCombo(ttk.Frame):
    """Combobox with type-to-filter for large lists (model picker)."""

    def __init__(self, parent: tk.Widget, field_def: FieldDef,
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_def = field_def
        self.on_change = on_change
        self.all_values = list(field_def.suggestions or field_def.enum_values or [])

        ttk.Label(self, text=field_def.key, width=20, anchor="w").pack(
            side=tk.LEFT, padx=(0, 8))

        self.var = tk.StringVar()
        self.combo = ttk.Combobox(
            self, textvariable=self.var, values=self.all_values,
            width=37,
        )
        self.combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.var.trace_add("write", lambda *_: self._filter())

        if on_change:
            self.combo.bind("<<ComboboxSelected>>", lambda _: on_change())

        ToolTip(self.combo, field_def.description)

    def _filter(self) -> None:
        typed = self.var.get().lower()
        if not typed:
            self.combo["values"] = self.all_values
        else:
            filtered = [v for v in self.all_values if typed in v.lower()]
            self.combo["values"] = filtered

    def get_value(self) -> str | None:
        val = self.var.get().strip()
        return val if val else None

    def set_value(self, value: Any) -> None:
        self.var.set(str(value) if value is not None else "")


class DynamicDictModal(tk.Toplevel):
    """Modal dialog for adding/editing a dynamic dict entry.

    Contains a name field (for new entries), form fields built from FieldDefs,
    and OK/Cancel buttons. Returns the entry data on OK.
    """

    def __init__(self, parent: tk.Widget, title: str,
                 entry_fields: list[FieldDef],
                 entry_name: str = "",
                 entry_data: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()

        self.result: dict | None = None
        self.result_name: str = ""
        self.entry_fields = entry_fields

        self.geometry("500x500")
        self.resizable(True, True)

        # Name field (editable only for new entries)
        name_frame = ttk.Frame(self)
        name_frame.pack(fill=tk.X, padx=12, pady=(12, 4))
        ttk.Label(name_frame, text="Name:", width=10).pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=entry_name)
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=30)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if entry_name:
            name_entry.config(state="readonly")

        # Scrollable form
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas)
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0), pady=4)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 12), pady=4)

        self.widgets: dict[str, Any] = {}
        for fd in entry_fields:
            w = build_field_widget(form_frame, fd)
            w.pack(fill=tk.X, pady=2, padx=4)
            self.widgets[fd.key] = w

        # Pre-populate if editing
        if entry_data:
            for fd in entry_fields:
                val = _get_dotted(entry_data, fd.key)
                if val is not None:
                    self.widgets[fd.key].set_value(val)

        # OK / Cancel buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=12, pady=(4, 12))
        ttk.Button(btn_frame, text="OK", command=self._on_ok, width=10).pack(
            side=tk.RIGHT, padx=(4, 0))
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel, width=10).pack(
            side=tk.RIGHT)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_ok(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            return
        self.result_name = name
        self.result = {}
        for fd in self.entry_fields:
            val = self.widgets[fd.key].get_value()
            if val is not None:
                _set_dotted(self.result, fd.key, val)
        self.destroy()

    def _on_cancel(self) -> None:
        self.result = None
        self.destroy()


class DynamicDictEditor(ttk.Frame):
    """Editor for dynamic key-value sections (providers, agents, commands, etc.).

    Shows a listbox of keys on the left. Add/Edit open modal dialogs.
    """

    def __init__(self, parent: tk.Widget, section_name: str,
                 entry_fields: list[FieldDef],
                 on_change: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.section_name = section_name
        self.entry_fields = entry_fields
        self.on_change = on_change
        self.data: dict[str, dict] = {}
        self.widgets: dict[str, Any] = {}

        # Left panel: key list
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        ttk.Label(left, text=f"{section_name} entries:").pack(anchor="w")
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
        ttk.Button(btn_frame, text="Edit", command=self._edit_key, width=5).pack(
            side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Del", command=self._del_key, width=5).pack(
            side=tk.LEFT)

        # Right panel: detail form (still shown for inline viewing)
        self.detail_frame = ttk.LabelFrame(self, text="Details", padding=8)
        self.detail_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_detail_form()

    def _build_detail_form(self) -> None:
        for child in self.detail_frame.winfo_children():
            child.destroy()
        self.widgets.clear()

        for fd in self.entry_fields:
            w = build_field_widget(self.detail_frame, fd, on_change=self._save_current)
            w.pack(fill=tk.X, pady=2)
            self.widgets[fd.key] = w

    def _on_select(self, event: tk.Event) -> None:
        sel = self.key_listbox.curselection()
        if not sel:
            return
        key = self.key_listbox.get(sel[0])
        entry_data = self.data.get(key, {})
        for fd in self.entry_fields:
            widget = self.widgets[fd.key]
            val = _get_dotted(entry_data, fd.key)
            widget.set_value(val)

    def _save_current(self) -> None:
        sel = self.key_listbox.curselection()
        if not sel:
            return
        key = self.key_listbox.get(sel[0])
        entry_data = self.data.get(key, {})
        for fd in self.entry_fields:
            widget = self.widgets[fd.key]
            val = widget.get_value()
            if val is not None:
                _set_dotted(entry_data, fd.key, val)
            else:
                _remove_dotted(entry_data, fd.key)
        self.data[key] = entry_data
        if self.on_change:
            self.on_change()

    def _add_key(self) -> None:
        key = self.new_key_var.get().strip()
        if not key:
            # Open modal for new entry
            modal = DynamicDictModal(
                self, f"Add {self.section_name} Entry",
                self.entry_fields,
            )
            self.wait_window(modal)
            if modal.result is not None:
                name = modal.result_name
                if name not in self.data:
                    self.data[name] = modal.result
                    self.key_listbox.insert(tk.END, name)
                    if self.on_change:
                        self.on_change()
            return

        if key not in self.data:
            self.data[key] = {}
            self.key_listbox.insert(tk.END, key)
            self.new_key_var.set("")
            if self.on_change:
                self.on_change()

    def _edit_key(self) -> None:
        sel = self.key_listbox.curselection()
        if not sel:
            return
        key = self.key_listbox.get(sel[0])
        entry_data = self.data.get(key, {})

        modal = DynamicDictModal(
            self, f"Edit {self.section_name}: {key}",
            self.entry_fields,
            entry_name=key,
            entry_data=entry_data,
        )
        self.wait_window(modal)
        if modal.result is not None:
            self.data[key] = modal.result
            self._on_select(None)
            if self.on_change:
                self.on_change()

    def _del_key(self) -> None:
        sel = self.key_listbox.curselection()
        if sel:
            key = self.key_listbox.get(sel[0])
            del self.data[key]
            self.key_listbox.delete(sel[0])
            for fd in self.entry_fields:
                self.widgets[fd.key].set_value(None)
            if self.on_change:
                self.on_change()

    def get_value(self) -> dict | None:
        return self.data if self.data else None

    def set_value(self, value: Any) -> None:
        self.data = dict(value) if isinstance(value, dict) else {}
        self.key_listbox.delete(0, tk.END)
        for key in self.data:
            self.key_listbox.insert(tk.END, key)


def _get_dotted(d: dict, key: str) -> Any:
    """Get value from dict using dotted key."""
    parts = key.split('.')
    current = d
    for p in parts:
        if not isinstance(current, dict) or p not in current:
            return None
        current = current[p]
    return current


def _set_dotted(d: dict, key: str, value: Any) -> None:
    """Set value in dict using dotted key."""
    parts = key.split('.')
    current = d
    for p in parts[:-1]:
        if p not in current or not isinstance(current[p], dict):
            current[p] = {}
        current = current[p]
    current[parts[-1]] = value


def _remove_dotted(d: dict, key: str) -> None:
    """Remove value from dict using dotted key."""
    parts = key.split('.')
    current = d
    for p in parts[:-1]:
        if not isinstance(current, dict) or p not in current:
            return
        current = current[p]
    if isinstance(current, dict):
        current.pop(parts[-1], None)


def build_field_widget(parent: tk.Widget, field_def: FieldDef,
                       on_change: Callable | None = None) -> Any:
    """Create the appropriate widget for a field definition.

    Args:
        parent: Parent tkinter widget.
        field_def: Field definition describing the config key.
        on_change: Callback when value changes.

    Returns:
        The created widget instance.
    """
    if field_def.field_type == FieldType.BOOLEAN:
        return LabeledCheck(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.ENUM and len(field_def.enum_values) <= 5:
        return RadioGroup(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.ENUM:
        return LabeledCombo(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.STRING_OR_BOOL:
        return LabeledStringOrBool(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.STRING_LIST:
        return StringListEditor(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.KEY_VALUE_MAP:
        return KeyValueEditor(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.OBJECT:
        return ObjectEditor(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.INTEGER and (
        field_def.min_value is not None or field_def.max_value is not None
    ):
        return LabeledSpinbox(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.NUMBER and (
        field_def.min_value is not None and field_def.max_value is not None
        and field_def.max_value <= 1.0
    ):
        return LabeledSlider(parent, field_def, on_change=on_change)
    elif field_def.field_type == FieldType.STRING and field_def.suggestions:
        return LabeledSuggest(parent, field_def, on_change=on_change)
    else:
        return LabeledEntry(parent, field_def, on_change=on_change)

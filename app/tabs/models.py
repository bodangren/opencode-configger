"""Enhanced model explorer widget with search, filtering, and live refresh."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from app.model_loader import ModelLoadError, ModelLoader, ModelMap


class EnhancedModelExplorer(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        on_pick_model: Callable[[str, str], None] | None = None,
        auto_refresh: bool = True,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.on_pick_model = on_pick_model
        self._loader = ModelLoader()
        self._models: ModelMap = {}
        self.provider_vars: dict[str, tk.BooleanVar] = {}

        self._build_header()
        self._build_provider_filter()
        self._build_tree()
        self._build_sidebar()
        self._build_loading_state()

        if auto_refresh:
            self.refresh()

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Label(header, text="Enhanced Model Explorer",
                  font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)

        self.refresh_button = ttk.Button(
            header, text="Refresh", command=self.refresh
        )
        self.refresh_button.pack(side=tk.RIGHT)

        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=8, pady=(0, 4))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_var.trace_add("write", lambda *_: self._on_search_changed())

    def _build_provider_filter(self) -> None:
        self.provider_frame = ttk.Frame(self)
        self.provider_frame.pack(fill=tk.X, padx=8, pady=(0, 4))

    def _build_tree(self) -> None:
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        self.tree = ttk.Treeview(tree_frame, columns=("name",), show="tree headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._on_tree_select())
        self.tree.bind("<Double-1>", lambda _e: self._apply_selection("model"))

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

    def _build_sidebar(self) -> None:
        side = ttk.Frame(self)
        side.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 0), before=self.provider_frame)

        self.selection_var = tk.StringVar(value="Selected: (none)")
        ttk.Label(side, textvariable=self.selection_var, wraplength=260).pack(
            anchor="w", pady=(0, 8)
        )

        self.btn_set_primary = ttk.Button(
            side, text="Set as Primary",
            command=lambda: self._apply_selection("model"),
            state="disabled",
        )
        self.btn_set_primary.pack(fill=tk.X, pady=(0, 6))

        self.btn_set_small = ttk.Button(
            side, text="Set as Small Model",
            command=lambda: self._apply_selection("small_model"),
            state="disabled",
        )
        self.btn_set_small.pack(fill=tk.X)

    def _build_loading_state(self) -> None:
        self._loading_label: ttk.Label | None = None
        self._loading_label = ttk.Label(self, text="Loading models...")
        self._loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def refresh(self) -> None:
        self._show_loading()
        self._loader.load_async(
            on_done=lambda models: self.after(0, lambda: self._on_load_success(models)),
            error_callback=lambda err: self.after(0, lambda: self._on_load_error(err)),
        )

    def _show_loading(self) -> None:
        if self._loading_label is None:
            self._loading_label = ttk.Label(self, text="Loading models...")
        self._loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self._hide_error_panel()

    def _hide_loading(self) -> None:
        if self._loading_label is not None:
            self._loading_label.place_forget()

    def _show_error_panel(self, message: str) -> None:
        self._hide_loading()
        if hasattr(self, "_error_label") and self._error_label is not None:
            self._error_label.destroy()
        self._error_label = ttk.Label(
            self, text=message, foreground="red", wraplength=400
        )
        self._error_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def _hide_error_panel(self) -> None:
        if hasattr(self, "_error_label") and self._error_label is not None:
            self._error_label.destroy()
            self._error_label = None

    def _on_load_success(self, models: ModelMap) -> None:
        self._hide_loading()
        self._models = models
        self._rebuild_provider_filter()
        self._populate_tree()

    def _on_load_error(self, err: ModelLoadError) -> None:
        self._show_error_panel(str(err))

    def _rebuild_provider_filter(self) -> None:
        for widget in self.provider_frame.winfo_children():
            widget.destroy()
        self.provider_vars.clear()

        providers = sorted(self._models.keys())
        for provider in providers:
            var = tk.BooleanVar(value=True)
            self.provider_vars[provider] = var
            cb = ttk.Checkbutton(
                self.provider_frame,
                text=f"{provider} ({len(self._models[provider])})",
                variable=var,
                command=lambda p=provider: self._on_provider_toggled(p),
            )
            cb.pack(side=tk.LEFT, padx=(0, 8))

    def _on_provider_toggled(self, provider: str) -> None:
        self._populate_tree()

    def _on_search_changed(self) -> None:
        self._populate_tree()

    def set_models(self, models: ModelMap) -> None:
        self._models = models
        self._rebuild_provider_filter()
        self._populate_tree()

    def _populate_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        search_term = self.search_var.get().lower()
        visible_providers = self._get_visible_providers()

        for provider in sorted(self._models.keys()):
            if provider not in visible_providers:
                continue

            models = sorted(set(self._models[provider]))
            if search_term:
                models = [m for m in models if search_term in m.lower()]

            if not models:
                continue

            provider_node = self.tree.insert("", tk.END, text=provider, open=True)
            for model in models:
                self.tree.insert(provider_node, tk.END, text=model)

        self._update_selection()

    def _get_visible_providers(self) -> set[str]:
        return {p for p, var in self.provider_vars.items() if var.get()}

    def _on_tree_select(self) -> None:
        model = self._selected_model()
        if model:
            self.selection_var.set(f"Selected: {model}")
            self.btn_set_primary.config(state="normal")
            self.btn_set_small.config(state="normal")
        else:
            self.selection_var.set("Selected: (none)")
            self.btn_set_primary.config(state="disabled")
            self.btn_set_small.config(state="disabled")

    def _selected_model(self) -> str | None:
        selection = self.tree.selection()
        if not selection:
            return None
        item_id = selection[0]
        if self.tree.parent(item_id) == "":
            return None
        return self.tree.item(item_id, "text")

    def _apply_selection(self, target: str) -> None:
        model = self._selected_model()
        if not model or self.on_pick_model is None:
            return
        self.on_pick_model(model, target)

    def _update_selection(self) -> None:
        self._on_tree_select()


class ModelsTab(EnhancedModelExplorer):
    """Legacy model browser tab — delegates to EnhancedModelExplorer for backward compatibility."""
    pass


def parse_models_json(raw: str) -> ModelMap:
    """Parse JSON model output into provider->models mapping."""
    from app.model_loader import _parse_models_output
    return _parse_models_output(raw)


def parse_models_text(raw: str) -> ModelMap:
    """Parse text model output into provider->models mapping."""
    import re
    grouped: ModelMap = {}
    for line in raw.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        match = re.search(r"([a-zA-Z0-9._-]+/[a-zA-Z0-9._:-]+)", cleaned)
        if not match:
            continue
        model_name = match.group(1)
        provider = model_name.split("/", 1)[0]
        grouped.setdefault(provider, []).append(model_name)
    return grouped


def fetch_models_from_cli() -> ModelMap:
    """Fetch available models by invoking OpenCode CLI."""
    from app.model_loader import ModelLoadError, ModelLoader
    loader = ModelLoader()
    try:
        return loader.load_sync()
    except ModelLoadError:
        raise RuntimeError("Unable to fetch models from OpenCode CLI")
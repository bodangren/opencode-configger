"""Model browser tab for OpenCode model discovery."""

import json
import re
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable


ModelMap = dict[str, list[str]]


def parse_models_json(raw: str) -> ModelMap:
    """Parse JSON model output into provider->models mapping."""
    data = json.loads(raw)
    grouped: ModelMap = {}

    if isinstance(data, dict):
        if all(isinstance(v, list) for v in data.values()):
            for provider, models in data.items():
                grouped[str(provider)] = [str(m) for m in models]
            return grouped

        models_list = data.get("models")
        if isinstance(models_list, list):
            for entry in models_list:
                if not isinstance(entry, dict):
                    continue
                model_name = str(entry.get("id") or entry.get("name") or "")
                if not model_name:
                    continue
                provider = model_name.split("/", 1)[0]
                grouped.setdefault(provider, []).append(model_name)
            return grouped

    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, str):
                model_name = entry
            elif isinstance(entry, dict):
                model_name = str(entry.get("id") or entry.get("name") or "")
            else:
                continue
            if not model_name:
                continue
            provider = model_name.split("/", 1)[0]
            grouped.setdefault(provider, []).append(model_name)
        return grouped

    raise ValueError("Unsupported JSON model payload")


def parse_models_text(raw: str) -> ModelMap:
    """Parse text model output into provider->models mapping."""
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
    commands = [
        ["opencode", "models", "--json"],
        ["opencode-cli", "models", "--json"],
        ["opencode", "models"],
        ["opencode-cli", "models"],
    ]

    last_error: Exception | None = None
    for command in commands:
        try:
            proc = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except Exception as exc:
            last_error = exc
            continue

        stdout = proc.stdout.strip()
        if not stdout:
            continue

        if "--json" in command:
            try:
                parsed = parse_models_json(stdout)
                if parsed:
                    return parsed
            except Exception:
                pass

        parsed = parse_models_text(stdout)
        if parsed:
            return parsed

    if last_error:
        raise RuntimeError(f"Unable to fetch models: {last_error}")
    raise RuntimeError("Unable to fetch models: no output from CLI")


class ModelsTab(ttk.Frame):
    """Tab to browse available models and set defaults."""

    def __init__(self, parent: tk.Widget,
                 on_pick_model: Callable[[str, str], None] | None = None,
                 auto_refresh: bool = True,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_pick_model = on_pick_model
        self.preferred_target = "model"

        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=(8, 6))
        ttk.Label(top, text="Model Browser",
                  font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(top, text="Refresh", command=self.refresh_models).pack(side=tk.RIGHT)

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.tree = ttk.Treeview(body, columns=("name",), show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", lambda _e: self._apply_selection(self.preferred_target))
        scroll = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_selection())

        side = ttk.Frame(body)
        side.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 0))

        self.selection_var = tk.StringVar(value="Selected: (none)")
        ttk.Label(side, textvariable=self.selection_var, wraplength=260).pack(
            anchor="w", pady=(0, 8)
        )
        self.btn_set_model = ttk.Button(
            side, text="Set as model",
            command=lambda: self._apply_selection("model"),
            state="disabled",
        )
        self.btn_set_model.pack(fill=tk.X, pady=(0, 6))
        self.btn_set_small = ttk.Button(
            side, text="Set as small_model",
            command=lambda: self._apply_selection("small_model"),
            state="disabled",
        )
        self.btn_set_small.pack(fill=tk.X)

        self.models: ModelMap = {}
        if auto_refresh:
            self.refresh_models()

    def _populate_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for provider in sorted(self.models.keys()):
            provider_id = self.tree.insert("", tk.END, text=provider, open=True)
            for model in sorted(set(self.models[provider])):
                self.tree.insert(provider_id, tk.END, text=model)
        self._update_selection()

    def _selected_model(self) -> str | None:
        selection = self.tree.selection()
        if not selection:
            return None
        item_id = selection[0]
        if self.tree.parent(item_id) == "":
            return None
        return self.tree.item(item_id, "text")

    def _update_selection(self) -> None:
        model = self._selected_model()
        if model:
            self.selection_var.set(f"Selected: {model}")
            self.btn_set_model.config(state="normal")
            self.btn_set_small.config(state="normal")
            return
        self.selection_var.set("Selected: (none)")
        self.btn_set_model.config(state="disabled")
        self.btn_set_small.config(state="disabled")

    def _apply_selection(self, target: str) -> None:
        model = self._selected_model()
        if not model or self.on_pick_model is None:
            return
        self.on_pick_model(model, target)

    def refresh_models(self) -> None:
        """Refresh model list by re-running OpenCode CLI."""
        try:
            self.models = fetch_models_from_cli()
        except Exception as exc:
            messagebox.showerror("Model fetch failed", str(exc))
            self.models = {}
        self._populate_tree()

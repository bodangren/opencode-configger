"""Templates tab — browse and apply pre-built configuration templates."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from app.template import Template, TemplateRepository


class TemplateCard(ttk.Frame):
    def __init__(self, parent: tk.Widget, template: Template, on_select: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.template = template
        self.on_select = on_select
        self._render()

    def _render(self) -> None:
        self.config(relief="solid", borderwidth=1, padding=8)

        name_label = ttk.Label(
            self,
            text=self.template.name,
            font=("TkDefaultFont", 11, "bold"),
        )
        name_label.pack(anchor="w")

        desc_label = ttk.Label(
            self,
            text=self.template.description,
            font=("TkDefaultFont", 9),
            foreground="#555",
            wraplength=280,
        )
        desc_label.pack(anchor="w", pady=(2, 4))

        tags_frame = ttk.Frame(self)
        tags_frame.pack(anchor="w", pady=(0, 4))
        for tag in self.template.tags[:4]:
            tag_lbl = ttk.Label(
                tags_frame,
                text=tag,
                font=("TkDefaultFont", 8),
                background="#e0e0e0",
                padding=(4, 1),
            )
            tag_lbl.pack(side="left", padx=(0, 4))

        apply_btn = ttk.Button(
            self,
            text="Apply Template",
            command=self._on_apply,
            width=18,
        )
        apply_btn.pack(anchor="e")

    def _on_apply(self) -> None:
        if self.on_select:
            self.on_select(self.template)


class TemplateDetailView(ttk.Frame):
    def __init__(self, parent: tk.Widget, template: Template | None = None, on_apply: Callable | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.template = template
        self.on_apply = on_apply
        self._render()

    def _render(self) -> None:
        if self.template is None:
            ttk.Label(self, text="Select a template to see details", font=("TkDefaultFont", 10)).pack(pady=20)
            return

        for w in self.winfo_children():
            w.destroy()

        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=8, pady=(8, 4))
        ttk.Label(header, text=self.template.name, font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)
        if self.template.built_in:
            badge = ttk.Label(header, text="Built-in", background="#4a90d9", foreground="white", padding=(6, 2))
            badge.pack(side=tk.RIGHT, padx=(0, 4))
        else:
            badge = ttk.Label(header, text="Custom", background="#5cb85c", foreground="white", padding=(6, 2))
            badge.pack(side=tk.RIGHT, padx=(0, 4))

        desc_lbl = ttk.Label(self, text=self.template.description, font=("TkDefaultFont", 9), foreground="#555", wraplength=320)
        desc_lbl.pack(anchor="w", padx=8, pady=(0, 8))

        tags_frame = ttk.Frame(self)
        tags_frame.pack(anchor="w", padx=8, pady=(0, 8))
        for tag in self.template.tags:
            ttk.Label(tags_frame, text=tag, font=("TkDefaultFont", 8), background="#e8e8e8", padding=(4, 2)).pack(side="left", padx=(0, 4))

        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill=tk.X, padx=8, pady=8)

        config_label = ttk.Label(self, text="Configuration Preview:", font=("TkDefaultFont", 10, "bold"))
        config_label.pack(anchor="w", padx=8)

        config_text = tk.Text(self, height=14, width=40, font=("Courier", 9), state="disabled", wrap="word")
        config_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))
        import json
        config_str = json.dumps(self.template.config, indent=2)
        config_text.config(state="normal")
        config_text.insert("1.0", config_str)
        config_text.config(state="disabled")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        apply_btn = ttk.Button(btn_frame, text="Apply Template", command=self._on_apply, style="Accent.TButton")
        apply_btn.pack(side="right")

    def set_template(self, template: Template | None) -> None:
        self.template = template
        self._render()

    def _on_apply(self) -> None:
        if self.template and self.on_apply:
            self.on_apply(self.template)


class TemplatesTab(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        on_change: Callable | None = None,
        on_apply_template: Callable | None = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.on_apply_template = on_apply_template
        self._repo = TemplateRepository()
        self._all_templates: list[Template] = []
        self._selected_template: Template | None = None

        self._build_header()
        self._build_search_bar()
        self._build_main_area()
        self._refresh_templates()

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        ttk.Label(header, text="Templates", font=("TkDefaultFont", 12, "bold")).pack(side=tk.LEFT)
        self.count_label = ttk.Label(header, text="", font=("TkDefaultFont", 9), foreground="#888")
        self.count_label.pack(side=tk.RIGHT, padx=(0, 8))
        ttk.Button(header, text="Import...", command=self._import_template).pack(side=tk.RIGHT, padx=(0, 8))
        ttk.Button(header, text="Refresh", command=self._refresh_templates).pack(side=tk.RIGHT)

    def _build_search_bar(self) -> None:
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_search())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.insert(0, "Search templates...")

        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(
            search_frame,
            textvariable=self.category_var,
            values=["All", "starter", "development", "specialized"],
            state="readonly",
            width=15,
        )
        category_combo.pack(side=tk.RIGHT, padx=(4, 0))
        category_combo.bind("<<ComboboxSelected>>", lambda *_: self._on_search())

    def _build_main_area(self) -> None:
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        list_frame = ttk.Frame(paned)
        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.template_list = ttk.Frame(canvas)
        self.template_list.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.template_list, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        paned.add(list_frame, weight=2)

        self.detail_view = TemplateDetailView(paned, on_apply=self._on_apply_template)
        paned.add(self.detail_view, weight=1)

    def load_config(self, data: dict) -> None:
        self._all_templates = self._repo.get_all_templates()
        self._render_list(self._all_templates)

    def save_config(self, data: dict) -> None:
        pass

    def _render_list(self, templates: list[Template]) -> None:
        for w in self.template_list.winfo_children():
            w.destroy()
        for tmpl in templates:
            card = TemplateCard(
                self.template_list,
                template=tmpl,
                on_select=self._on_select_template,
            )
            card.pack(fill=tk.X, pady=2, padx=4)
        self.count_label.config(text=f"{len(templates)} templates")

    def _on_search(self) -> None:
        query = self.search_var.get().strip()
        category = self.category_var.get()
        if query:
            results = self._repo.search_templates(query)
        else:
            results = self._all_templates
        if category != "All":
            results = [t for t in results if t.category == category]
        self._render_list(results)

    def _on_select_template(self, template: Template) -> None:
        self._selected_template = template
        self.detail_view.set_template(template)

    def _refresh_templates(self) -> None:
        self._all_templates = self._repo.get_all_templates()
        self._render_list(self._all_templates)

    def _import_template(self) -> None:
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Import Template",
            filetypes=[("JSONC files", "*.jsonc"), ("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            repo = TemplateRepository()
            from pathlib import Path
            tmpl = repo._load_template_file(Path(path), built_in=False)
            if tmpl is None:
                tk.messagebox.showerror("Import Error", "Failed to parse template file")
                return
            self._repo._custom.append(tmpl)
            self._refresh_templates()
            tk.messagebox.showinfo("Imported", f"Template '{tmpl.name}' imported successfully")
        except Exception as e:
            tk.messagebox.showerror("Import Error", f"Failed to import template:\n{e}")
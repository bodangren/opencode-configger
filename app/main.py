"""Application entry point for OpenCode Configger."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import ttkbootstrap as ttkb
    HAS_TTKBOOTSTRAP = True
except ImportError:
    ttkb = None  # type: ignore[assignment]
    HAS_TTKBOOTSTRAP = False

from app.config_io import (
    find_config_files,
    load_jsonc,
    new_config,
    new_tui_config,
    save_json,
)
from app.config_schema import validate_config
from app.config_io import preview_variable, substitute_variables
from app.dialogs.file_picker import choose_open_config, choose_save_config
from app.tabs.agents import AgentsTab
from app.tabs.commands import CommandsTab
from app.tabs.compaction import AdvancedTab
from app.tabs.formatters import FormattersTab
from app.tabs.general import GeneralTab
from app.tabs.lsp import LSPTab
from app.tabs.mcp import MCPServersTab
from app.tabs.models import ModelsTab
from app.tabs.providers import ProvidersTab
from app.tabs.server import ServerTab
from app.tabs.tui import TuiTab
from app.tabs.tools import ToolsTab


class ConfiggerApp:
    """Main OpenCode config editor application."""

    def __init__(self, root: tk.Tk):
        """Initialize the application.

        Args:
            root: Root Tk window.
        """
        self.root = root
        self.current_config_path: Path | None = None
        self.opencode_data: dict = {}
        self.is_dirty = False
        self._validation_errors: list[str] = []

        self.root.geometry("1000x700")
        self._build_menu()
        self._build_save_button()
        self._build_status_bar()
        self._build_tabs()
        self._bind_shortcuts()

        self._load_default_or_new()
        self._update_title()
        self._update_validation_state()

    def _build_save_button(self) -> None:
        """Create a Save button in the button bar."""
        self.save_btn = ttk.Button(
            self.root, text="Save", command=self.save_file, width=10,
        )
        self.save_btn.place(relx=1.0, rely=1.0, x=-8, y=-2, anchor="se")

    def _build_status_bar(self) -> None:
        """Create the status bar at the bottom of the window."""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_path_label = ttk.Label(
            self.status_bar, text="", anchor="w", padding=(4, 2),
        )
        self.status_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_error_label = ttk.Label(
            self.status_bar, text="", anchor="e", padding=(0, 2),
            foreground="#cc0000",
        )
        self.status_error_label.pack(side=tk.RIGHT, padx=(0, 8))

        self.status_dirty_label = ttk.Label(
            self.status_bar, text="", width=12, anchor="e", padding=(0, 2),
        )
        self.status_dirty_label.pack(side=tk.RIGHT, padx=(0, 8))

        self._update_status()

    def _update_status(self) -> None:
        """Refresh status bar with current file path and dirty state."""
        if self.current_config_path:
            path_text = str(self.current_config_path)
        else:
            path_text = "Untitled"
        self.status_path_label.config(text=path_text)

        if self.is_dirty:
            self.status_dirty_label.config(text="MODIFIED")
        else:
            self.status_dirty_label.config(text="Saved")

    def _set_dirty(self, dirty: bool) -> None:
        """Set dirty state and refresh title and status bar.

        Args:
            dirty: New dirty state.
        """
        self.is_dirty = dirty
        self._update_title()
        self._update_status()

    def _update_validation_state(self) -> None:
        """Run validation and update save button state + status bar."""
        data = self._collect_from_tabs()
        self._validation_errors = validate_config(data)
        error_count = len(self._validation_errors)

        if error_count == 0:
            self.status_error_label.config(text="")
            self.save_btn.config(state=tk.NORMAL)
        else:
            self.status_error_label.config(
                text=f"{error_count} error{'s' if error_count > 1 else ''} — fix before saving"
            )
            self.save_btn.config(state=tk.DISABLED)

    def _build_menu(self) -> None:
        """Create the application menu bar."""
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)

        file_menu.add_command(label="New", accelerator="Ctrl+N",
                              command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O",
                              command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S",
                              command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S",
                              command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", accelerator="Ctrl+Q",
                              command=self.quit_app)

        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Preview Variables...",
                               command=self._preview_variables)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        self.root.config(menu=menu_bar)

    def _preview_variables(self) -> None:
        """Show a dialog with all variable substitutions in the current config."""
        data = self._collect_from_tabs()
        all_vars: dict[str, str] = {}

        def scan_value(key: str, val: Any) -> None:
            if isinstance(val, str):
                vars_in_val = preview_variable(val)
                for raw, resolved in vars_in_val.items():
                    all_vars[f"{key} = {raw}"] = resolved

        def scan_dict(prefix: str, d: dict) -> None:
            for k, v in d.items():
                full_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    scan_dict(full_key, v)
                elif isinstance(v, str):
                    scan_value(full_key, v)
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, str):
                            scan_value(f"{full_key}[{i}]", item)

        scan_dict("", data)

        if not all_vars:
            messagebox.showinfo("Variable Preview", "No variables found in the current configuration.")
            return

        lines = []
        for key_raw, resolved in all_vars.items():
            lines.append(f"{key_raw}")
            lines.append(f"  -> {resolved}")
            lines.append("")

        dialog = tk.Toplevel(self.root)
        dialog.title("Variable Substitution Preview")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        text = tk.Text(dialog, wrap=tk.WORD, font=("Courier New", 10))
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        text.insert("1.0", "\n".join(lines))
        text.config(state=tk.DISABLED)

        btn = ttk.Button(dialog, text="Close", command=dialog.destroy, width=15)
        btn.pack(pady=8)

    def _build_tabs(self) -> None:
        """Create notebook and currently implemented tabs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.general_tab = GeneralTab(
            self.notebook,
            on_change=self._on_change,
            on_pick_model_request=self._open_model_picker,
        )
        self.server_tab = ServerTab(self.notebook, on_change=self._on_change)
        self.advanced_tab = AdvancedTab(self.notebook, on_change=self._on_change)
        self.providers_tab = ProvidersTab(self.notebook, on_change=self._on_change)
        self.agents_tab = AgentsTab(self.notebook, on_change=self._on_change)
        self.tools_tab = ToolsTab(self.notebook, on_change=self._on_change)
        self.commands_tab = CommandsTab(self.notebook, on_change=self._on_change)
        self.formatters_tab = FormattersTab(self.notebook, on_change=self._on_change)
        self.mcp_tab = MCPServersTab(self.notebook, on_change=self._on_change)
        self.lsp_tab = LSPTab(self.notebook, on_change=self._on_change)
        self.tui_tab = TuiTab(self.notebook, on_change=self._on_change)
        self.models_tab = ModelsTab(self.notebook, on_pick_model=self._apply_model)

        self.notebook.add(self.general_tab, text="General")
        self.notebook.add(self.server_tab, text="Server")
        self.notebook.add(self.advanced_tab, text="Advanced")
        self.notebook.add(self.providers_tab, text="Providers")
        self.notebook.add(self.agents_tab, text="Agents")
        self.notebook.add(self.tools_tab, text="Permissions")
        self.notebook.add(self.commands_tab, text="Commands")
        self.notebook.add(self.formatters_tab, text="Formatters")
        self.notebook.add(self.mcp_tab, text="MCP")
        self.notebook.add(self.lsp_tab, text="LSP")
        self.notebook.add(self.tui_tab, text="TUI")
        self.notebook.add(self.models_tab, text="Models")

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts for file actions."""
        self.root.bind("<Control-n>", lambda _: self.new_file())
        self.root.bind("<Control-o>", lambda _: self.open_file())
        self.root.bind("<Control-s>", lambda _: self.save_file())
        self.root.bind("<Control-S>", lambda _: self.save_file_as())
        self.root.bind("<Control-q>", lambda _: self.quit_app())
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def _update_title(self) -> None:
        """Update window title with current file and dirty state."""
        path_label = "Untitled"
        if self.current_config_path:
            path_label = str(self.current_config_path)
        dirty_marker = " *" if self.is_dirty else ""
        self.root.title(f"OpenCode Configger - {path_label}{dirty_marker}")

    def _set_dirty(self, dirty: bool) -> None:
        """Set dirty state and refresh title and status bar.

        Args:
            dirty: New dirty state.
        """
        self.is_dirty = dirty
        self._update_title()
        self._update_status()

    def _on_change(self) -> None:
        """Mark document as modified when any field changes."""
        self._set_dirty(True)
        self._update_validation_state()

    def _load_default_or_new(self) -> None:
        """Load default config if found, otherwise initialize a new one."""
        locations = find_config_files()
        default_path = (
            locations.get("project")
            or locations.get("env")
            or locations.get("global")
        )
        if default_path:
            self._load_config_path(default_path)
        else:
            self.opencode_data = new_config()
            self._load_tabs(self.opencode_data)

        tui_path = locations.get("tui_global")
        if tui_path:
            try:
                tui_data = load_jsonc(tui_path)
                if isinstance(tui_data, dict):
                    self.tui_tab.current_path = tui_path
                    self.tui_tab.load_config(tui_data)
                    self.tui_tab._refresh_path_label()
            except Exception:
                pass
        else:
            self.tui_tab.load_config(new_tui_config())

        self._set_dirty(False)
        self._update_validation_state()

    def _load_tabs(self, data: dict) -> None:
        """Load config data into all instantiated tabs.

        Args:
            data: opencode.json data.
        """
        self.general_tab.load_config(data)
        self.server_tab.load_config(data)
        self.advanced_tab.load_config(data)
        self.providers_tab.load_config(data)
        self.agents_tab.load_config(data)
        self.tools_tab.load_config(data)
        self.commands_tab.load_config(data)
        self.formatters_tab.load_config(data)
        self.mcp_tab.load_config(data)
        self.lsp_tab.load_config(data)
        self._update_validation_state()

    def _apply_model(self, model_name: str, target: str) -> None:
        """Apply model chosen in model browser to general settings.

        Args:
            model_name: Fully-qualified model name (provider/model).
            target: Either "model" or "small_model".
        """
        if target not in {"model", "small_model"}:
            return
        self.general_tab.set_field_value(target, model_name)
        self.notebook.select(self.general_tab)

    def _open_model_picker(self, target: str) -> None:
        """Switch to models tab for picking a target model field."""
        self.models_tab.preferred_target = target
        self.notebook.select(self.models_tab)

    def _collect_from_tabs(self) -> dict:
        """Collect values from tabs into a config dictionary.

        Returns:
            Serialized opencode configuration.
        """
        output = {}
        output["$schema"] = self.opencode_data.get(
            "$schema", "https://opencode.ai/config.json"
        )
        self.general_tab.save_config(output)
        self.server_tab.save_config(output)
        self.advanced_tab.save_config(output)
        self.providers_tab.save_config(output)
        self.agents_tab.save_config(output)
        self.tools_tab.save_config(output)
        self.commands_tab.save_config(output)
        self.formatters_tab.save_config(output)
        self.mcp_tab.save_config(output)
        self.lsp_tab.save_config(output)
        return output

    def _load_config_path(self, path: Path) -> bool:
        """Load a config file from disk.

        Args:
            path: Path to an opencode.json file.

        Returns:
            True when load succeeds, False otherwise.
        """
        try:
            data = load_jsonc(path)
        except FileNotFoundError:
            messagebox.showerror("Open failed", f"File not found: {path}")
            return False
        except Exception as exc:
            messagebox.showerror("Open failed", f"Could not load file:\n{exc}")
            return False

        if not isinstance(data, dict):
            messagebox.showerror("Open failed", "Config file must be a JSON object")
            return False

        self.current_config_path = path
        self.opencode_data = data
        self._load_tabs(data)
        self._set_dirty(False)
        self._update_validation_state()
        return True

    def _confirm_discard(self) -> bool:
        """Ask user to save/discard unsaved changes.

        Returns:
            True when the caller can continue with the pending action.
        """
        if not self.is_dirty:
            return True

        answer = messagebox.askyesnocancel(
            "Unsaved changes",
            "You have unsaved changes. Save before continuing?",
        )
        if answer is None:
            return False
        if answer:
            return self.save_file()
        return True

    def new_file(self) -> None:
        """Start a new config file."""
        if not self._confirm_discard():
            return
        self.current_config_path = None
        self.opencode_data = new_config()
        self._load_tabs(self.opencode_data)
        self._set_dirty(False)

    def open_file(self) -> None:
        """Open a config file selected by the user."""
        if not self._confirm_discard():
            return
        initial_dir = self.current_config_path.parent if self.current_config_path else None
        selected = choose_open_config(initial_dir=initial_dir)
        if not selected:
            return
        self._load_config_path(selected)

    def save_file(self) -> bool:
        """Save current config to disk after validation.

        Returns:
            True when save succeeds, False otherwise.
        """
        if self.current_config_path is None:
            return self.save_file_as()

        data = self._collect_from_tabs()
        errors = validate_config(data)
        if errors:
            error_text = "\n".join(f"  - {e}" for e in errors)
            messagebox.showerror(
                "Validation Error",
                f"Configuration has the following errors:\n\n{error_text}\n\n"
                "Please fix these issues before saving.",
            )
            return False
        try:
            save_json(self.current_config_path, data)
        except Exception as exc:
            messagebox.showerror("Save failed", f"Could not save file:\n{exc}")
            return False

        self.opencode_data = data
        self._set_dirty(False)
        return True

    def save_file_as(self) -> bool:
        """Save current config to a selected path.

        Returns:
            True when save succeeds, False otherwise.
        """
        selected = choose_save_config(initial_path=self.current_config_path)
        if not selected:
            return False

        self.current_config_path = selected
        ok = self.save_file()
        if ok:
            self._update_title()
        return ok

    def quit_app(self) -> None:
        """Exit application after unsaved-change guard."""
        if not self._confirm_discard():
            return
        self.root.destroy()


def main() -> None:
    """Run the desktop GUI application."""
    if HAS_TTKBOOTSTRAP:
        root = ttkb.Window(themename="darkly")
    else:
        root = tk.Tk()
    ConfiggerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""File picker dialogs for OpenCode config files."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog


def choose_open_config(initial_dir: Path | None = None) -> Path | None:
    """Open a file dialog for selecting an OpenCode config file.

    Args:
        initial_dir: Optional starting directory.

    Returns:
        Selected path, or None if canceled.
    """
    parent = tk._default_root
    selected = filedialog.askopenfilename(
        parent=parent,
        title="Open OpenCode Config",
        initialdir=str(initial_dir) if initial_dir else None,
        filetypes=[
            ("JSON files", "*.json"),
            ("JSONC files", "*.jsonc"),
            ("All files", "*.*"),
        ],
    )
    if not selected:
        return None
    return Path(selected)


def choose_save_config(
    initial_path: Path | None = None,
    default_filename: str = "opencode.json",
) -> Path | None:
    """Open a save dialog for an OpenCode config file.

    Args:
        initial_path: Optional current path to suggest.

    Returns:
        Selected path, or None if canceled.
    """
    parent = tk._default_root
    initial_dir = initial_path.parent if initial_path else None
    initial_file = initial_path.name if initial_path else default_filename

    selected = filedialog.asksaveasfilename(
        parent=parent,
        title="Save OpenCode Config",
        initialdir=str(initial_dir) if initial_dir else None,
        initialfile=initial_file,
        defaultextension=".json",
        filetypes=[
            ("JSON files", "*.json"),
            ("JSONC files", "*.jsonc"),
            ("All files", "*.*"),
        ],
    )
    if not selected:
        return None
    return Path(selected)

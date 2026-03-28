"""JSONC (JSON with comments) reader/writer for OpenCode config files."""

import json
import os
import re
from pathlib import Path
from typing import Any


def strip_jsonc_comments(text: str) -> str:
    """Remove single-line (//) and multi-line (/* */) comments from JSONC.

    Also strips trailing commas before } and ].
    """
    result = []
    i = 0
    in_string = False
    while i < len(text):
        # Handle string literals
        if text[i] == '"' and (i == 0 or text[i - 1] != '\\'):
            in_string = not in_string
            result.append(text[i])
            i += 1
            continue

        if in_string:
            result.append(text[i])
            i += 1
            continue

        # Single-line comment
        if i + 1 < len(text) and text[i] == '/' and text[i + 1] == '/':
            while i < len(text) and text[i] != '\n':
                i += 1
            continue

        # Multi-line comment
        if i + 1 < len(text) and text[i] == '/' and text[i + 1] == '*':
            i += 2
            while i + 1 < len(text) and not (text[i] == '*' and text[i + 1] == '/'):
                i += 1
            i += 2  # skip */
            continue

        result.append(text[i])
        i += 1

    stripped = ''.join(result)
    # Remove trailing commas before } or ]
    stripped = re.sub(r',\s*([}\]])', r'\1', stripped)
    return stripped


def load_jsonc(file_path: str | Path) -> dict[str, Any]:
    """Load a JSONC file and return parsed dict.

    Args:
        file_path: Path to the JSONC file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the JSON is malformed after stripping comments.
    """
    path = Path(file_path)
    text = path.read_text(encoding='utf-8')
    clean = strip_jsonc_comments(text)
    if not clean.strip():
        return {}
    return json.loads(clean)


def save_json(file_path: str | Path, data: dict[str, Any]) -> None:
    """Save a dict as formatted JSON with $schema as first key.

    Args:
        file_path: Path to write the JSON file.
        data: Configuration dictionary to save.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure $schema is first by building ordered output
    ordered = {}
    if '$schema' in data:
        ordered['$schema'] = data['$schema']
    for key, value in data.items():
        if key != '$schema':
            ordered[key] = value

    text = json.dumps(ordered, indent=2, ensure_ascii=False)
    path.write_text(text + '\n', encoding='utf-8')


def find_config_files() -> dict[str, Path | None]:
    """Find OpenCode config files in standard locations.

    Returns:
        Dict with keys 'global', 'project', 'env' mapping to found paths or None.
    """
    locations = {}

    # Global config
    global_path = Path.home() / '.config' / 'opencode' / 'opencode.json'
    locations['global'] = global_path if global_path.exists() else None

    # Project config (current directory)
    project_path = Path.cwd() / 'opencode.json'
    locations['project'] = project_path if project_path.exists() else None

    # Environment variable
    env_path = os.environ.get('OPENCODE_CONFIG')
    if env_path:
        p = Path(env_path)
        locations['env'] = p if p.exists() else None
    else:
        locations['env'] = None

    # Global TUI config
    tui_global = Path.home() / '.config' / 'opencode' / 'tui.json'
    locations['tui_global'] = tui_global if tui_global.exists() else None

    return locations


def new_config() -> dict[str, Any]:
    """Return a minimal new opencode.json config."""
    return {
        '$schema': 'https://opencode.ai/config.json',
    }


def new_tui_config() -> dict[str, Any]:
    """Return a minimal new tui.json config."""
    return {
        '$schema': 'https://opencode.ai/tui.json',
    }

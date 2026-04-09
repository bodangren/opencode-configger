# Tech Stack

## Language
- **Python 3.10+** — widely available, cross-platform, rich standard library

## UI Framework
- **tkinter** (standard library) — zero external dependencies, ships with Python
- **ttkbootstrap** (optional enhancement) — modern themed widgets if available, graceful fallback to plain ttk

## Data Handling
- **json** (standard library) — read/write config files
- Custom JSONC parser for comment-preserving read/write (OpenCode uses JSONC)

## Testing
- **pytest** — test runner and assertions
- **pytest-cov** — coverage reporting

## Project Structure
```
opencode-configger/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point, main window
│   ├── config_schema.py     # Schema definitions for all config keys
│   ├── config_io.py         # Load/save JSONC files
│   ├── widgets.py           # Reusable form widgets
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── general.py       # General settings tab
│   │   ├── providers.py     # Provider configuration tab
│   │   ├── agents.py        # Agent configuration tab
│   │   ├── tools.py         # Tools & permissions tab
│   │   ├── server.py        # Server settings tab
│   │   ├── mcp.py           # MCP servers tab
│   │   ├── commands.py      # Commands tab
│   │   ├── tui.py           # TUI settings tab (theme, keybinds, scroll)
│   │   └── models.py        # Model browser tab
│   └── dialogs/
│       ├── __init__.py
│       └── file_picker.py   # Config file open/save dialogs
├── tests/
│   ├── __init__.py
│   ├── test_config_schema.py
│   ├── test_config_io.py
│   └── test_widgets.py
├── conductor/               # Conductor project management
├── requirements.txt         # pytest, pytest-cov, ttkbootstrap (optional)
└── pyproject.toml           # Project metadata
```

## Development Commands

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
python -m app.main
```

### Test
```bash
CI=true pytest --cov=app --cov-report=html
```

### Lint
```bash
python -m py_compile app/main.py
```

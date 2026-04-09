# Implementation Plan: MVP — Core Config Editor

## Phase 1: Project Foundation

- [ ] **1.1** Create project scaffolding (pyproject.toml, requirements.txt, app package structure)
- [ ] **1.2** Implement JSONC reader/writer (`config_io.py`) — parse JSON with comments, preserve $schema
- [ ] **1.3** Define config schema constants (`config_schema.py`) — all keys, types, defaults, descriptions, enums
- [x] **1.4** Write tests for config_io and config_schema

## Phase 2: Core UI Framework

- [x] **2.1** Create main window with tabbed notebook layout (`main.py`)
- [ ] **2.2** Build reusable form widgets (`widgets.py`) — labeled entry, dropdown, checkbox, list editor, tooltip
- [x] **2.3** Implement config load/save dialogs (`dialogs/file_picker.py`)
- [x] **2.4** Wire up File menu: New, Open, Save, Save As, Quit
- [x] **2.5** Write tests for widgets

## Phase 3: Config Tabs — Static Sections

- [x] **3.1** General settings tab (model, small_model, default_agent, logLevel, username, share, autoupdate, snapshot)
- [x] **3.2** Server settings tab (port, hostname, mdns, mdnsDomain, cors list)
- [x] **3.3** Compaction settings tab (auto, prune, reserved)
- [x] **3.4** Watcher & instructions tab (ignore patterns, instruction paths)
- [x] **3.5** Write tests for static tabs

## Phase 4: Config Tabs — Dynamic Sections

- [x] **4.1** Provider configuration tab (add/remove providers, edit options and models)
- [x] **4.2** Agent configuration tab (add/remove agents, all agent fields)
- [x] **4.3** Tools & permissions tab (per-tool allow/ask/deny dropdowns)
- [x] **4.4** Commands tab (add/remove commands with template, description, agent, model)
- [x] **4.5** Formatter tab (add/remove formatters with command, extensions, env)
- [x] **4.6** MCP servers tab (add/remove MCP servers)
- [x] **4.7** Write tests for dynamic tabs

## Phase 5: TUI Config & Model Browser

- [x] **5.1** TUI settings tab (theme, scroll_speed, scroll_acceleration, diff_style)
- [x] **5.2** Keybinding editor (all 87+ keybind slots, searchable)
- [x] **5.3** Model browser tab (run opencode-cli models, group by provider, click to set)
- [x] **5.4** Write tests for TUI and model browser tabs

## Phase 6: Polish & Integration

- [ ] **6.1** Config validation before save (type checking, enum validation, required fields)
- [ ] **6.2** Status bar with current file path and dirty indicator
- [ ] **6.3** Variable substitution preview ({env:...}, {file:...})
- [ ] **6.4** Final integration testing and coverage check

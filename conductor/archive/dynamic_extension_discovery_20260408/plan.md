# Implementation Plan: Dynamic Extension Discovery

## Phase 1: Scanner Infrastructure

- [x] Task: Implement `PluginScanner` module (`app/scanners/plugin_scanner.py`).
  - [x] Run `npm ls --json --depth=0` in a subprocess with a 3-second timeout.
  - [x] Filter packages whose name starts with `opencode-plugin-` or has `opencode-plugin` in keywords.
  - [x] Return list of `PluginDescriptor(name, config_keys=[])` objects.
  - [x] On timeout or error, return empty list and log warning.
- [x] Task: Implement `McpScanner` module (`app/scanners/mcp_scanner.py`).
  - [x] Read the `mcp` section of the currently loaded config dict.
  - [x] For each stdio-type MCP entry, run `<command> --help` with 3-second timeout and parse output for `--config-*` style flags.
  - [x] Return list of `McpDescriptor(server_name, config_keys=[])` objects.
- [x] Task: Write unit tests for both scanners using mocked subprocess calls.
- [x] Task: Conductor — User Manual Verification 'Phase 1: Scanner Infrastructure' (Protocol in workflow.md)
  [checkpoint: 95% coverage, 15/15 tests pass]

## Phase 2: Extensions Tab

- [x] Task: Create "Extensions" tab in main window (`app/tabs/extensions.py`).
  - [x] On tab open, call both scanners (in background thread).
  - [x] Render one collapsible section per discovered plugin/MCP server.
  - [x] Sections with no machine-readable keys show a raw JSON text area for that config block.
  - [x] Show loading spinner while scanning; show "No extensions found" if list is empty.
- [x] Task: Add "Refresh Extensions" button that re-runs scanners without restarting.
- [x] Task: Write tab tests using fixture descriptor data (no real subprocesses).
- [x] Task: Conductor — User Manual Verification 'Phase 2: Extensions Tab' (Protocol in workflow.md)
  [checkpoint: integrated into main.py, Extensions tab visible in notebook]

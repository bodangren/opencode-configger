# Implementation Plan: Dynamic Extension Discovery

## Phase 1: Scanner Infrastructure

- [ ] Task: Implement `PluginScanner` module (`app/scanners/plugin_scanner.py`).
  - [ ] Run `npm ls --json --depth=0` in a subprocess with a 3-second timeout.
  - [ ] Filter packages whose name starts with `opencode-plugin-` or has `opencode-plugin` in keywords.
  - [ ] Return list of `PluginDescriptor(name, config_keys=[])` objects.
  - [ ] On timeout or error, return empty list and log warning.
- [ ] Task: Implement `McpScanner` module (`app/scanners/mcp_scanner.py`).
  - [ ] Read the `mcp` section of the currently loaded config dict.
  - [ ] For each stdio-type MCP entry, run `<command> --help` with 3-second timeout and parse output for `--config-*` style flags.
  - [ ] Return list of `McpDescriptor(server_name, config_keys=[])` objects.
- [ ] Task: Write unit tests for both scanners using mocked subprocess calls.
- [ ] Task: Conductor — User Manual Verification 'Phase 1: Scanner Infrastructure' (Protocol in workflow.md)

## Phase 2: Extensions Tab

- [ ] Task: Create "Extensions" tab in main window (`app/tabs/extensions.py`).
  - [ ] On tab open, call both scanners (in background thread).
  - [ ] Render one collapsible section per discovered plugin/MCP server.
  - [ ] Sections with no machine-readable keys show a raw JSON text area for that config block.
  - [ ] Show loading spinner while scanning; show "No extensions found" if list is empty.
- [ ] Task: Add "Refresh Extensions" button that re-runs scanners without restarting.
- [ ] Task: Write tab tests using fixture descriptor data (no real subprocesses).
- [ ] Task: Conductor — User Manual Verification 'Phase 2: Extensions Tab' (Protocol in workflow.md)

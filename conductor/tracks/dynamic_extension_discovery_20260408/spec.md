# Track: Dynamic Extension Discovery

## Overview

OpenCode's plugin and MCP server ecosystem is growing rapidly. Currently, users must know the config keys for each plugin in advance. This track lets the GUI scan locally installed plugins and running/configured MCP servers and surface their config requirements as first-class form sections — so users never have to hunt through plugin READMEs.

## Functional Requirements

- A `PluginScanner` module inspects the local npm/npx environment to discover installed OpenCode plugins by querying their published `opencode-plugin` metadata (if available).
- A `McpScanner` module reads the currently loaded `opencode.json` MCP entries and, for stdio servers, runs `--help` or reads any advertised schema endpoint to extract configurable keys.
- Discovered plugin/MCP config keys are rendered as a collapsible "Extensions" tab section, using the same widget mapping as core config keys.
- Discovery runs once on app startup and can be re-triggered with a "Refresh Extensions" button.
- If a plugin exposes no machine-readable schema, a fallback raw JSON editor is shown for that plugin's config block.

## Non-Functional Requirements

- Scanner must time-out after 3 seconds per plugin/server to prevent UI hangs.
- Scanning must not modify any config file.
- Graceful fallback when no plugins are installed.

## Acceptance Criteria

- [ ] `PluginScanner` returns a list of discovered plugin config descriptors (mocked in tests).
- [ ] `McpScanner` returns config descriptors for at least one stdio MCP server entry.
- [ ] Discovered keys render in the "Extensions" tab using appropriate widgets.
- [ ] Scanning times out after 3 s per source and logs a warning.
- [ ] "Refresh Extensions" button re-runs discovery without restarting the app.
- [ ] No existing tests regress.
- [ ] Coverage ≥80% on scanner modules (using mocks for subprocess calls).

## Out of Scope

- Publishing or installing plugins from within the GUI.
- SSE/streamable-http MCP introspection (stdio only for now).

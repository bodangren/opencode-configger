# Specification: MVP — Core Config Editor

## Overview
Build a Python GUI application that provides a form-based editor for OpenCode's `opencode.json` and `tui.json` configuration files. The app reads/writes JSONC (JSON with comments), validates against the known schema, and exposes every configuration section through a tabbed interface.

## Configuration Schema Summary

### opencode.json — Top-Level Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `$schema` | string | `"https://opencode.ai/config.json"` | JSON Schema URL |
| `logLevel` | enum | — | DEBUG, INFO, WARN, ERROR |
| `model` | string | — | Primary model (format: `provider/model`) |
| `small_model` | string | — | Lightweight model for tasks |
| `default_agent` | string | — | Default agent name |
| `username` | string | — | Display name |
| `snapshot` | boolean | `true` | Enable change tracking |
| `share` | enum | `"manual"` | manual, auto, disabled |
| `autoupdate` | boolean or `"notify"` | `true` | Auto-update behavior |
| `disabled_providers` | string[] | `[]` | Provider IDs to exclude |
| `enabled_providers` | string[] | `[]` | Allowlisted provider IDs |
| `plugin` | string[] | `[]` | npm plugin identifiers |
| `instructions` | string[] | `[]` | Paths/globs to instruction files |

### opencode.json — Server Object

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `server.port` | integer | `0` | Listen port (>0) |
| `server.hostname` | string | `"127.0.0.1"` | Listen address |
| `server.mdns` | boolean | `false` | Enable mDNS discovery |
| `server.mdnsDomain` | string | `"opencode.local"` | Custom mDNS domain |
| `server.cors` | string[] | `[]` | Allowed CORS origins |

### opencode.json — Provider Object

Dynamic keys. Each provider entry:

| Key | Type | Description |
|-----|------|-------------|
| `provider.<id>.npm` | string | npm package for the provider SDK |
| `provider.<id>.name` | string | Display name |
| `provider.<id>.options.baseURL` | string | API endpoint URL |
| `provider.<id>.options.timeout` | number | Request timeout (ms), default 300000 |
| `provider.<id>.options.chunkTimeout` | number | Stream chunk timeout (ms) |
| `provider.<id>.options.setCacheKey` | boolean | Enforce cache key |
| `provider.<id>.models` | object | Map of model ID → model options |

### opencode.json — Agent Object

Dynamic keys. Each agent entry:

| Key | Type | Description |
|-----|------|-------------|
| `agent.<id>.model` | string | Model reference |
| `agent.<id>.prompt` | string | System prompt |
| `agent.<id>.description` | string | Agent description |
| `agent.<id>.mode` | enum | subagent, primary, all |
| `agent.<id>.hidden` | boolean | Hide from UI |
| `agent.<id>.disable` | boolean | Disable agent |
| `agent.<id>.color` | string | Hex color or theme color |
| `agent.<id>.steps` | integer | Max steps (>0) |
| `agent.<id>.temperature` | number | Sampling temperature |
| `agent.<id>.top_p` | number | Top-p sampling |

### opencode.json — Permission Object

Per-tool permission. Tools: read, edit, glob, grep, list, bash, task, external_directory, question, webfetch, websearch, codesearch, lsp, skill.

Values: `"allow"`, `"ask"`, `"deny"`

### opencode.json — Command Object

Dynamic keys. Each command:

| Key | Type | Description |
|-----|------|-------------|
| `command.<id>.template` | string | **Required.** Command template |
| `command.<id>.description` | string | Command description |
| `command.<id>.agent` | string | Agent to use |
| `command.<id>.model` | string | Model to use |

### opencode.json — Formatter Object

Dynamic keys. Each formatter:

| Key | Type | Description |
|-----|------|-------------|
| `formatter.<id>.disabled` | boolean | Disable formatter |
| `formatter.<id>.command` | string | Formatter command |
| `formatter.<id>.extensions` | string[] | File extensions |
| `formatter.<id>.environment` | object | Env vars for formatter |

### opencode.json — Compaction Object

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `compaction.auto` | boolean | `true` | Auto-compact when full |
| `compaction.prune` | boolean | `true` | Remove old outputs |
| `compaction.reserved` | number | — | Token buffer |

### opencode.json — Watcher Object

| Key | Type | Description |
|-----|------|-------------|
| `watcher.ignore` | string[] | Glob patterns to exclude |

### opencode.json — Skills Object

| Key | Type | Description |
|-----|------|-------------|
| `skills.paths` | string[] | Local skill paths |
| `skills.urls` | string[] | Remote skill URLs |

### tui.json Schema

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `$schema` | string | `"https://opencode.ai/tui.json"` | Schema URL |
| `theme` | string | — | UI theme identifier |
| `scroll_speed` | number | — | Scroll velocity (min 0.001) |
| `scroll_acceleration.enabled` | boolean | — | Enable scroll acceleration |
| `diff_style` | enum | — | auto, stacked |
| `keybinds.*` | string | — | 87+ keybinding slots (see full list in app) |

### Variable Substitution
Config values support:
- `{env:VARIABLE_NAME}` — environment variable
- `{file:path/to/file}` — file contents (relative, absolute, or ~)

## Acceptance Criteria

1. **Load**: App reads `opencode.json` and `tui.json` from a user-selected path or default locations
2. **Display**: Every config key above is editable through appropriate widgets (text fields, dropdowns, checkboxes, lists)
3. **Validate**: Before save, validate types and constraints (enums, min values, required fields)
4. **Save**: Write valid JSONC back to disk, preserving `$schema` key
5. **Models**: Model browser tab shows output of `opencode-cli models` grouped by provider
6. **Dynamic sections**: Providers, agents, commands, formatters support add/remove/edit of arbitrary keys
7. **Tooltips**: Every field has a tooltip with its description
8. **Cross-platform**: Works on Linux, macOS, Windows with Python 3.10+

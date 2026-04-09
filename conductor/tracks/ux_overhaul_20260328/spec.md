# Specification: UX Overhaul — Schema Correction & Modern Widgets

## Overview

The current config editor works but looks and feels like a Windows 95 registry editor — every field is a plain text entry regardless of what it accepts. Users have no way to discover valid values, no visual cues about field types, and no guardrails against invalid input.

This track has two goals:
1. **Fix the schema** — our `config_schema.py` was built from incomplete documentation and has significant errors compared to the actual OpenCode v1.3.x source (TypeScript/Zod, `anomalyco/opencode` repo, `packages/opencode/src/config/config.ts`).
2. **Replace generic text boxes with appropriate widgets** — dropdowns, radio buttons, checkboxes, spinboxes, color pickers, multi-select, modals, and collapsible sections so the UI actually helps people configure OpenCode.

## Authoritative Schema Source

The npm `opencode` v1.3.3 is the current version. Its config is defined in Zod schemas:
- Main config: `packages/opencode/src/config/config.ts` → `Config.Info`
- TUI config: `packages/opencode/src/config/tui-schema.ts` → `TuiInfo`
- TUI options: `packages/opencode/src/config/tui-schema.ts` → `TuiOptions`
- Keybinds: `packages/opencode/src/config/config.ts` → `Config.Keybinds`
- Log levels: `packages/opencode/src/util/log.ts` → `Log.Level`

## Schema Corrections Required

### Fields to fix in `config_schema.py`

#### Permission tools list
**Current (wrong)**: 15 tools — `read, edit, glob, grep, list, bash, task, external_directory, question, webfetch, websearch, codesearch, lsp, skill, doom_loop`
**Correct**: 16 tools — add `todowrite`. Also: `question` and `todowrite` accept only `PermissionAction` (flat enum), while `read, edit, glob, grep, list, bash, task, external_directory, lsp, skill` accept `PermissionRule` (flat enum OR pattern-record).

#### MCP server fields
**Current (wrong)**:
- `type` enum: `stdio`, `sse`, `streamable-http`
- `command`: string
- `args`: string[]
- `url`: string
- `enabled`: boolean

**Correct** — discriminated union on `type`:

**Local** (`type: "local"`):
| Key | Type | Description |
|-----|------|-------------|
| `type` | literal `"local"` | Connection type |
| `command` | **string[]** | Command AND args combined in one array |
| `environment` | Record<string,string> | Env vars for the server |
| `enabled` | boolean | Enable/disable on startup |
| `timeout` | int (positive, ms) | Request timeout, default 5000 |

**Remote** (`type: "remote"`):
| Key | Type | Description |
|-----|------|-------------|
| `type` | literal `"remote"` | Connection type |
| `url` | string | Server URL |
| `enabled` | boolean | Enable/disable on startup |
| `headers` | Record<string,string> | HTTP headers |
| `oauth` | object or `false` | OAuth config (clientId, clientSecret, scope) or false to disable |
| `timeout` | int (positive, ms) | Request timeout, default 5000 |

#### Provider fields
**Current (wrong)**: `npm, name, options.baseURL, options.timeout, options.chunkTimeout, options.setCacheKey`

**Correct**:
| Key | Type | Description |
|-----|------|-------------|
| `options.apiKey` | string | API key |
| `options.baseURL` | string | Custom API endpoint |
| `options.enterpriseUrl` | string | GitHub Enterprise URL (copilot) |
| `options.setCacheKey` | boolean | Enable promptCacheKey |
| `options.timeout` | int or `false` | Request timeout ms (default 300000), false to disable |
| `options.chunkTimeout` | int (positive) | SSE chunk timeout ms |
| `whitelist` | string[] | Allowed model IDs |
| `blacklist` | string[] | Blocked model IDs |
| `models` | Record<string, object> | Per-model config overrides and variant settings |
| `disabled` | boolean | Disable provider entirely |

Remove: `npm`, `name` (these don't exist in the current schema).

#### Agent fields
**Current (mostly right, missing some)**:
- Add: `variant` (string), `permission` (Permission object), `options` (Record<string,any>)
- `maxSteps` is deprecated alias for `steps`
- `color` enum values: `primary, secondary, accent, success, warning, error, info`

#### Well-known agent names
The schema defines named slots: `build`, `plan`, `general`, `explore`, `title`, `summary`, `compaction` — plus arbitrary custom agents via `.catchall(Agent)`.

#### Formatter `command` field
**Current (wrong)**: `command` is `FieldType.STRING`
**Correct**: `command` is `string[]` (array, not string)

#### Command fields
**Missing**: `subtask` (boolean) and `model` field

#### Missing sections entirely
| Section | Type | Description |
|---------|------|-------------|
| `lsp` | Record<string, LSPConfig> or `false` | Language Server Protocol configs |
| `experimental` | object | Feature flags (disable_paste_summary, batch_tool, openTelemetry, primary_tools, continue_loop_on_deny, mcp_timeout) |
| `enterprise` | object | Enterprise settings (url) |

#### LSP config entry
| Key | Type | Description |
|-----|------|-------------|
| `command` | string[] (required unless disabled) | LSP server command |
| `extensions` | string[] (required for custom servers) | File extensions |
| `disabled` | boolean | Disable server |
| `env` | Record<string,string> | Environment variables |
| `initialization` | Record<string,any> | Init options |

Or simply `{ disabled: true }` to disable a built-in server.

#### TUI schema corrections
- `theme`: free string (not enum) — suggest known themes but allow custom
- `plugin`: same PluginSpec format as main config
- `plugin_enabled`: Record<string, boolean> — toggle individual plugins
- Keybind defaults: every slot now has a documented default from source (e.g., `leader` = `"ctrl+x"`, `app_exit` = `"ctrl+c,ctrl+d,<leader>q"`)

### Keybind Defaults (complete, from source)
| Slot | Default |
|------|---------|
| `leader` | `ctrl+x` |
| `app_exit` | `ctrl+c,ctrl+d,<leader>q` |
| `editor_open` | `<leader>e` |
| `theme_list` | `<leader>t` |
| `sidebar_toggle` | `<leader>b` |
| `scrollbar_toggle` | `none` |
| `username_toggle` | `none` |
| `status_view` | `<leader>s` |
| `session_export` | `<leader>x` |
| `session_new` | `<leader>n` |
| `session_list` | `<leader>l` |
| `session_timeline` | `<leader>g` |
| `session_fork` | `none` |
| `session_rename` | `ctrl+r` |
| `session_delete` | `ctrl+d` |
| `stash_delete` | `ctrl+d` |
| `model_provider_list` | `ctrl+a` |
| `model_favorite_toggle` | `ctrl+f` |
| `session_share` | `none` |
| `session_unshare` | `none` |
| `session_interrupt` | `escape` |
| `session_compact` | `<leader>c` |
| `messages_page_up` | `pageup,ctrl+alt+b` |
| `messages_page_down` | `pagedown,ctrl+alt+f` |
| `messages_line_up` | `ctrl+alt+y` |
| `messages_line_down` | `ctrl+alt+e` |
| `messages_half_page_up` | `ctrl+alt+u` |
| `messages_half_page_down` | `ctrl+alt+d` |
| `messages_first` | `ctrl+g,home` |
| `messages_last` | `ctrl+alt+g,end` |
| `messages_next` | `none` |
| `messages_previous` | `none` |
| `messages_last_user` | `none` |
| `messages_copy` | `<leader>y` |
| `messages_undo` | `<leader>u` |
| `messages_redo` | `<leader>r` |
| `messages_toggle_conceal` | `<leader>h` |
| `tool_details` | `none` |
| `model_list` | `<leader>m` |
| `model_cycle_recent` | `f2` |
| `model_cycle_recent_reverse` | `shift+f2` |
| `model_cycle_favorite` | `none` |
| `model_cycle_favorite_reverse` | `none` |
| `command_list` | `ctrl+p` |
| `agent_list` | `<leader>a` |
| `agent_cycle` | `tab` |
| `agent_cycle_reverse` | `shift+tab` |
| `variant_cycle` | `ctrl+t` |
| `input_clear` | `ctrl+c` |
| `input_paste` | `ctrl+v` |
| `input_submit` | `return` |
| `input_newline` | `shift+return,ctrl+return,alt+return,ctrl+j` |
| `input_move_left` | `left,ctrl+b` |
| `input_move_right` | `right,ctrl+f` |
| `input_move_up` | `up` |
| `input_move_down` | `down` |
| `input_select_left` | `shift+left` |
| `input_select_right` | `shift+right` |
| `input_select_up` | `shift+up` |
| `input_select_down` | `shift+down` |
| `input_line_home` | `ctrl+a` |
| `input_line_end` | `ctrl+e` |
| `input_select_line_home` | `ctrl+shift+a` |
| `input_select_line_end` | `ctrl+shift+e` |
| `input_visual_line_home` | `alt+a` |
| `input_visual_line_end` | `alt+e` |
| `input_select_visual_line_home` | `alt+shift+a` |
| `input_select_visual_line_end` | `alt+shift+e` |
| `input_buffer_home` | `home` |
| `input_buffer_end` | `end` |
| `input_select_buffer_home` | `shift+home` |
| `input_select_buffer_end` | `shift+end` |
| `input_delete_line` | `ctrl+shift+d` |
| `input_delete_to_line_end` | `ctrl+k` |
| `input_delete_to_line_start` | `ctrl+u` |
| `input_backspace` | `backspace,shift+backspace` |
| `input_delete` | `ctrl+d,delete,shift+delete` |
| `input_undo` | `ctrl+-,super+z` |
| `input_redo` | `ctrl+.,super+shift+z` |
| `input_word_forward` | `alt+f,alt+right,ctrl+right` |
| `input_word_backward` | `alt+b,alt+left,ctrl+left` |
| `input_select_word_forward` | `alt+shift+f,alt+shift+right` |
| `input_select_word_backward` | `alt+shift+b,alt+shift+left` |
| `input_delete_word_forward` | `alt+d,alt+delete,ctrl+delete` |
| `input_delete_word_backward` | `ctrl+w,ctrl+backspace,alt+backspace` |
| `history_previous` | `up` |
| `history_next` | `down` |
| `session_child_first` | `<leader>down` |
| `session_child_cycle` | `right` |
| `session_child_cycle_reverse` | `left` |
| `session_parent` | `up` |
| `terminal_suspend` | `ctrl+z` |
| `terminal_title_toggle` | `none` |
| `tips_toggle` | `<leader>h` |
| `plugin_manager` | `none` |
| `display_thinking` | `none` |

## UX Widget Mapping

Every field should use the most specific widget available:

| Field Type | Widget | When |
|-----------|--------|------|
| Enum with ≤5 values | **Radio buttons** | share, diff_style, autoupdate |
| Enum with >5 values | **Dropdown (Combobox)** | logLevel, agent mode, permission values |
| Boolean | **Checkbox** | All bool fields |
| Integer with bounds | **Spinbox** | port, steps, timeout, reserved |
| Number (0–1 range) | **Slider + entry** | temperature, top_p |
| Number (unbounded) | **Spinbox** | scroll_speed |
| Hex color | **Color picker button + entry** | agent color |
| Theme color enum | **Dropdown** | agent color (when not hex) |
| String list | **Tag-style list with add/remove** | cors, ignore, extensions, whitelist, blacklist |
| Record<string,string> | **Key-value table with add/remove** | environment, headers, env |
| Model ID | **Searchable dropdown** | model, small_model, agent model, command model |
| Multiline string | **Text area** | agent prompt, command template |
| Permission tool | **Dropdown** per tool or pattern rule editor | permission section |
| Dynamic dict (agents, providers, etc.) | **List + modal for add/edit** | Instead of cramped split-pane |

## Visual Design Requirements

1. **Apply ttkbootstrap dark theme** (e.g., `darkly` or `superhero`) — it's already a dependency
2. **Section headers with collapsible frames** — group related fields visually
3. **Modal dialogs for add/edit** on dynamic dicts — providers, agents, MCP, commands, formatters, LSP
4. **Inline validation indicators** — red border / icon on invalid fields
5. **Default value indicators** — show placeholder text for default values, grey out unset fields
6. **Search/filter** — on permission tools list, keybind editor, model picker
7. **Tab icons or colored labels** — distinguish main config tabs from TUI tab

## Acceptance Criteria

1. Every field in the corrected schema renders with the appropriate widget type (not a plain text entry)
2. Enum fields use dropdowns or radio buttons — users cannot enter invalid values
3. Boolean fields are checkboxes
4. Numeric fields with constraints use spinboxes or sliders with enforcement
5. MCP editor handles the local/remote discriminated union with a type selector that swaps the form
6. Provider editor shows the correct fields (options.apiKey, options.baseURL, etc.)
7. Agent editor includes all fields (variant, permission, color picker)
8. Permission editor shows all 16 tools with correct value types (action vs rule)
9. LSP and experimental sections are present
10. Keybind editor shows default values as placeholders
11. ttkbootstrap theme is applied and the app doesn't look like a registry editor
12. All existing tests still pass after schema changes
13. New tests cover the corrected schema definitions and new widget types

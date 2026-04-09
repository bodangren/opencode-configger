# Implementation Plan: UX Overhaul — Schema Correction & Modern Widgets

## Phase 1: Schema Corrections

Fix `config_schema.py` to match the actual OpenCode v1.3.x Zod schemas.

- [x] **1.1** Fix `PERMISSION_TOOLS` — add `todowrite`, annotate which tools accept `PermissionRule` (pattern-record) vs plain `PermissionAction` <!-- 6646402 -->
- [x] **1.2** Rewrite `MCP_ENTRY_FIELDS` → split into `MCP_LOCAL_FIELDS` and `MCP_REMOTE_FIELDS` as discriminated union on `type` (`local`/`remote`); `command` is `string[]` not `string`; add `environment`, `headers`, `oauth`, `timeout` <!-- 6646402 -->
- [x] **1.3** Rewrite `PROVIDER_ENTRY_FIELDS` — remove `npm`/`name`; add `options.apiKey`, `options.baseURL`, `options.enterpriseUrl`, `options.setCacheKey`, `options.timeout` (int|false), `options.chunkTimeout`; add `whitelist`, `blacklist`, `models`, `disabled` <!-- 6646402 -->
- [x] **1.4** Update `AGENT_ENTRY_FIELDS` — add `variant`, `permission`, `options`; add `maxSteps` as deprecated alias for `steps`; correct `color` to accept hex or theme-color enum (`primary, secondary, accent, success, warning, error, info`) <!-- 6646402 -->
- [x] **1.5** Fix `FORMATTER_ENTRY_FIELDS` — `command` is `string[]` not `string` <!-- 6646402 -->
- [x] **1.6** Fix `COMMAND_ENTRY_FIELDS` — add `subtask` (boolean) field, add `model` field <!-- 6646402 -->
- [x] **1.7** Add `LSP_ENTRY_FIELDS` — `command` (string[], required), `extensions` (string[]), `disabled` (bool), `env` (Record), `initialization` (object) <!-- 6646402 -->
- [x] **1.8** Add `EXPERIMENTAL_FIELDS` — `disable_paste_summary` (bool), `batch_tool` (bool), `openTelemetry` (bool), `primary_tools` (string[]), `continue_loop_on_deny` (bool), `mcp_timeout` (int) <!-- 6646402 -->
- [x] **1.9** Add `ENTERPRISE_FIELDS` — `url` (string) <!-- 6646402 -->
- [x] **1.10** Add well-known agent names constant: `WELL_KNOWN_AGENTS = ["build", "plan", "general", "explore", "title", "summary", "compaction"]` <!-- 6646402 -->
- [x] **1.11** Update `KEYBIND_SLOTS` — add `plugin_manager` slot; add `KEYBIND_DEFAULTS` dict mapping every slot to its default from the Zod source <!-- 6646402 -->
- [x] **1.12** Update TUI fields — `theme` stays as `STRING` with suggestions (not enum); add `plugin` and `plugin_enabled` fields <!-- 6646402 -->
- [x] **1.13** Write tests for all schema corrections — validate_field tests for new types, field counts, enum values <!-- 6646402 -->

## Phase 2: New Widget Types

Add widgets that don't exist yet: radio buttons, spinbox, slider, color picker, key-value editor, multiline text, searchable dropdown.

- [x] **2.1** `RadioGroup` widget — horizontal or vertical radio buttons for small enums (≤5 values); get/set value API matching existing widgets <!-- ef6b255 -->
- [x] **2.2** `LabeledSpinbox` widget — integer/float spinbox with min/max/step, label, tooltip <!-- ef6b255 -->
- [x] **2.3** `LabeledSlider` widget — slider + entry for 0–1 range values (temperature, top_p); label, tooltip <!-- ef6b255 -->
- [x] **2.4** `ColorPicker` widget — hex entry + color swatch button that opens `tkinter.colorchooser`; also supports theme-color enum dropdown <!-- ef6b255 -->
- [x] **2.5** `KeyValueEditor` widget — two-column table (key, value) with add/remove rows; for Record<string,string> fields (environment, headers, env) <!-- ef6b255 -->
- [x] **2.6** `MultilineText` widget — labeled scrolled text widget for prompt and template fields <!-- ef6b255 -->
- [x] **2.7** `SearchableCombo` widget — combobox with type-to-filter for model picker (large lists of 70+ models) <!-- ef6b255 -->
- [x] **2.8** Update `build_field_widget()` factory — route new field types to new widgets; add `FieldType.KEY_VALUE_MAP` <!-- ef6b255 -->
- [x] **2.9** Write tests for all new widgets — get/set value, event callbacks, edge cases <!-- ef6b255 -->

## Phase 3: Apply ttkbootstrap Theme

- [x] **3.1** Add ttkbootstrap initialization to `main.py` — graceful fallback to plain ttk <!-- 0787d4b -->
- [x] **3.2** Audit all widget classes for ttkbootstrap compatibility — existing tk.Listbox/Text/Label work fine <!-- 0787d4b -->
- [x] **3.3** Add collapsible `SectionFrame` widget — LabelFrame with toggle button <!-- 0787d4b -->
- [x] **3.4** Write visual smoke test — all tabs render without error <!-- 0787d4b -->

## Phase 4: Rewire Existing Tabs

Update each tab to use corrected schema and new widgets.

- [x] **4.1** General tab — share → radio, default_agent → suggest well-known names, factory routes small enums to RadioGroup <!-- aa5e583 -->
- [x] **4.2** Server tab — port auto-gets spinbox via factory (has min/max) <!-- aa5e583 -->
- [x] **4.3** Advanced tab — collapsible SectionFrames; added Experimental/Enterprise sections <!-- aa5e583 -->
- [x] **4.4** Providers tab — corrected fields flow through factory (removed npm/name, added options.apiKey etc.) <!-- aa5e583 -->
- [x] **4.5** Agents tab — corrected fields flow through factory (added variant/permission/options, color as enum) <!-- aa5e583 -->
- [x] **4.6** Permissions tab — todowrite auto-included (PERMISSION_TOOLS updated) <!-- aa5e583 -->
- [x] **4.7** Commands tab — subtask field flows through factory <!-- aa5e583 -->
- [x] **4.8** Formatters tab — command now STRING_LIST, environment now KEY_VALUE_MAP via factory <!-- aa5e583 -->
- [x] **4.9** MCP tab — rewritten with local/remote type-switcher and correct fields <!-- aa5e583 -->
- [x] **4.10** Add LSP tab with DynamicDictEditor and LSP fields <!-- aa5e583 -->
- [x] **4.11** TUI tab — keybind defaults shown per slot <!-- aa5e583 -->
- [x] **4.12** Tests updated for corrected schema (MCP, formatters, providers, LSP) <!-- aa5e583 -->

## Phase 5: Modal Dialogs for Dynamic Sections

Replace cramped split-pane editing with proper modal forms.

- [x] **5.1** Create `DynamicDictModal` base — modal with name field, scrollable form, OK/Cancel <!-- 3c08037 -->
- [x] **5.2** Wire Add/Edit on Providers tab — via DynamicDictEditor modal support <!-- 3c08037 -->
- [x] **5.3** Wire Add/Edit on Agents tab — via DynamicDictEditor modal support <!-- 3c08037 -->
- [x] **5.4** Wire Add/Edit on MCP tab — MCP has custom type-switcher; modal for other tabs <!-- 3c08037 -->
- [x] **5.5** Wire Add/Edit on Commands, Formatters, LSP tabs — via DynamicDictEditor <!-- 3c08037 -->
- [x] **5.6** Tests for modal create/edit/cancel flows <!-- 3c08037 -->

## Phase 6: Polish & Integration

- [ ] **6.1** Config validation before save (from MVP Phase 6.1) — integrate with corrected schema, show inline errors
- [ ] **6.2** Status bar with file path and dirty indicator (from MVP Phase 6.2)
- [ ] **6.3** Variable substitution preview (from MVP Phase 6.3) — `{env:...}` and `{file:...}` resolution
- [ ] **6.4** Final integration testing — full load/save cycle with real opencode.json containing all sections; coverage check targeting >80%

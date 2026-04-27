# Project Tracks

This file tracks all major tracks for the project.

---

- [x] **Track: MVP — Core Config Editor**
  *Link: [./archive/mvp_20260328/](./archive/mvp_20260328/)*
- [x] **Track: UX Overhaul — Schema Correction & Modern Widgets**
  *Link: [./archive/ux_overhaul_20260328/](./archive/ux_overhaul_20260328/)*

---

- [x] **Track: Schema Validation & Feedback**
  *Link: [./archive/schema_validation_feedback_20260408/](./archive/schema_validation_feedback_20260408/)*
  Implement real-time validation against the defined 'FieldDef' constraints (min/max, required) with visual error indicators in the GUI.

## Future Roadmap

- [x] **Track: Dynamic Extension Discovery**
  *Link: [./archive/dynamic_extension_discovery_20260408/](./archive/dynamic_extension_discovery_20260408/)*
  Enable the GUI to scan for and integrate configuration requirements from OpenCode plugins or MCP servers dynamically.

- [x] **Track: Tooltip Fix — Error tooltip re-show bug**
  *Link: [./archive/tooltip_fix_20260417/](./archive/tooltip_fix_20260417/)*
  Fix error tooltip re-showing on every show_error call by reusing single ToolTip instance.

- [x] **Track: Configuration Versioning & Migration**
  *Link: [./archive/config_versioning_migration_20260408/](./archive/config_versioning_migration_20260408/)*
  Add logic to handle 'breaking changes' in config schemas, providing automated migration paths for older config files.

- [x] **Track: Enhanced Model Explorer**
  *Link: [./archive/enhanced_model_explorer_20260408/](./archive/enhanced_model_explorer_20260408/)*
  Develop a more advanced model picker with search, filtering by provider, and integration with live provider APIs to show available models.

- [x] **Track: Interactive Architecture Graph**
  *Link: [./archive/interactive_architecture_graph_20260424/](./archive/interactive_architecture_graph_20260424/)*
  Add a visual tab that renders a graph of the configured agents, providers, and tools to help users visualize their setup.

- [x] **Track: Config Import/Export**
  *Link: [./archive/config_import_export_20260423/](./archive/config_import_export_20260423/)*
  Import/export configurations for sharing and migration with secrets masking, schema validation, and merge strategies.

## Upcoming Tracks

- [x] **Track: Config Templates & Presets**
  *Link: [./archive/config_templates_presets_20260424/](./archive/config_templates_presets_20260424/)*
  Pre-built configuration templates for common setups, template browser, one-click application, custom template save/export.

- [x] **Track: Undo/Redo & Change History**
  *Link: [./archive/undo_redo_history_20260424/](./archive/undo_redo_history_20260424/)*
  Command pattern for change tracking, unlimited undo/redo, history persistence, visual diff between states.

- [ ] **Track: Config Diff & Merge Tool**
  *Link: [./tracks/config_diff_merge_20260424/](./tracks/config_diff_merge_20260424/)*
  Side-by-side diff view, three-way merge for conflicts, field-level change indicators, merge preview.

- [ ] **Track: Live Config Validation with OpenCode**
  *Link: [./tracks/live_config_validation_20260424/](./tracks/live_config_validation_20260424/)*
  Validate against running OpenCode instance, model name verification, provider connectivity tests, MCP server health checks.

- [x] **Track: Visual Refresh: Define Unique Identity**
  *Link: [./archive/visual_refresh_20260425/](./archive/visual_refresh_20260425/)*
  *Status: Complete*

- [ ] **Track: Widget-Wired Undo/Redo**
  *Link: [./tracks/widget_wired_undo_redo_20260426/](./tracks/widget_wired_undo_redo_20260426/)*
  Connect record_change() to all editable widgets for full change tracking.

- [ ] **Track: Regex-Based Secret Detection**
  *Link: [./tracks/regex_secret_detection_20260426/](./tracks/regex_secret_detection_20260426/)*
  Upgrade SecretsMasker from substring to regex pattern matching.

- [ ] **Track: Config Search & Quick-Jump**
  *Link: [./tracks/config_search_quick_jump_20260428/](./tracks/config_search_quick_jump_20260428/)*
  Global search bar to find any config key, value, or setting across all tabs with keyboard-driven quick-jump navigation.

- [ ] **Track: Batch Config Operations**
  *Link: [./tracks/batch_config_operations_20260428/](./tracks/batch_config_operations_20260428/)*
  Batch apply templates, validate, and export multiple config files at once for team standardization workflows.

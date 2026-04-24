# Lessons Learned

> This file is curated working memory, not an append-only log. Keep it at or below **50 lines**.
> Remove or condense entries that are no longer relevant to near-term planning.

## Architecture & Design
<!-- Decisions made that future tracks should be aware of -->

## Recurring Gotchas
<!-- Problems encountered repeatedly; save future tracks from the same pain -->

## Patterns That Worked Well
- `validate_field` + `validate_config` pattern: field-level validators composed into a full-config validator — easy to test in isolation and extend per section.
- Error border via tk.Frame `highlightbackground` + `highlightthickness` — cleaner than ttk styling for dynamic error states.
- Per-widget error state (show_error/clear_error) wired via on_change callback chain — works consistently across Entry, Combo, Spinbox, Check.
- PluginScanner + McpScanner: scanner modules return descriptor objects; separation of scanning from rendering keeps logic testable.
- SecretsMasker: substring-based keyword matching (case-insensitive) over regex for default patterns — simpler and faster for common secret names.
- Merge strategies (replace/overlay/selective) as pure functions operating on dicts — easy to unit test independently of UI.
- `strip_jsonc_comments` handles both trailing commas and JSONC comments uniformly, so import path doesn't need separate JSONC detection.

## Implementation Notes
- Plan spec uses `min`/`max`/`choices` but implementation uses `min_value`/`max_value`/`enum_values` — semantics are identical, just naming difference. No refactoring needed.
- Widget error state uses wrapper tk.Frame with red highlightborder around the inner ttk widget.
- Validation state (_validation_errors) maintained in main.py and updated via _update_validation_state() on every change, load, and after _collect_from_tabs.
- Extensions tab runs scanners synchronously on the main thread (3s timeout per plugin/MCP is fast enough to not block UI significantly).
- CollapsibleSection uses +/– prefix on header label to indicate expand/collapse state.
- ToolTip bindings (<Enter>, <Leave>) persist after _hide; creating new ToolTip instances on each show_error caused rogue tooltips on hover. Fix: reuse single instance with set_text + show instead of creating new.
- config_export.py and config_import.py are standalone modules — export is pure data transformation, import returns ImportResult with errors/unknown_keys/is_valid.
- Merge dialog (Phase 4) uses compute_diff to show conflicts as checkboxes with current vs imported values.

## Planning Improvements
- Phase 3 (Save Guard & Status Bar): 3 tasks completed in one session — status bar label, save button disable/enable, and integration tests.
- Phase 6 (Polish) tasks were smaller than Phase 1-5 (Schema + Widgets) — 4 tasks completed in one session vs multi-session phases earlier.
- Phase 6.1-6.3 (validation, status bar, variable preview) were already implemented before Phase 6 started — plan was ahead of marks.
- Phase 2 (Widget Error States): 4 tasks completed in one session — show_error/clear_error pattern is consistent across widget types.
- Phase 1 (Scanner Infrastructure) + Phase 2 (Extensions Tab) for Dynamic Extension Discovery track: 5 commits across 2 phases completed in one session.
- Config Import/Export track: All 4 phases completed in one session — export/import/masking and UI integration all landed cleanly with 93 tests passing.
- Config Versioning track: 3 phases completed in one session — detect_version scans formatter/mcp commands for string values, MigrationRegistry stores direct-migration pairs, _find_next_version is a placeholder for future chain migrations.
- Enhanced Model Explorer track: ModelLoader extracted from tab, async loading with callbacks, ModelsTab backward-compatible via inheritance from EnhancedModelExplorer.
- Interactive Architecture Graph track: Phase 1 (GraphData + HierarchicalLayout) completed — GraphData uses directed edges (source→target), layer assignment via longest-path from sources (nodes with no incoming edges at layer 0).
- Architecture tab: GraphCanvas sets _graph reference during load_graph() before redraw() so helper methods (highlight_neighbors, show_tooltip, clear_highlight) can reference the stored graph. Tooltip Toplevel uses overrideredirect(True) for borderless floating appearance.
- Config Templates track: Template dataclass + TemplateRepository — built-in templates in app/templates/builtin/*.jsonc, custom templates in ~/.configger/templates/. Template.to_dict() includes built_in and filename fields for round-trip JSONC serialization.
- Undo/Redo track: Command pattern with CommandHistory (undo/redo stacks) + HistoryManager (persistence). _bind_shortcuts for Ctrl+Z/Ctrl+Shift+Z, _build_edit_buttons for Undo/Redo buttons. record_change() method available but not yet wired to widgets.
# Track: Config Import/Export

## Overview

Add import and export functionality so users can share configurations or migrate between environments. Export produces JSON/JSONC with optional secrets masking. Import validates against the schema and supports merge strategies (replace, overlay, selective). Exchange works via file or clipboard.

## Functional Requirements

### Export
- Export the current config as JSON or JSONC.
- Preserve comments when exporting JSONC.
- Optional secrets masking: replace values matching configurable patterns (e.g., `*API_KEY*`, `*TOKEN*`, `*SECRET*`) with `***REDACTED***`.
- Masking patterns are user-configurable with sensible defaults.
- Export to file path or system clipboard.

### Import
- Import a config from a JSON/JSONC file or clipboard text.
- Validate imported config against the current schema before applying.
- Report validation errors with line numbers and field paths.
- Support three merge strategies:
  - **Replace**: discard current config, use imported config entirely.
  - **Overlay**: deep-merge imported config on top of current config (imported wins on conflict).
  - **Selective**: present a diff UI and let the user pick which keys to import.
- Reject imports with unknown top-level keys unless the user explicitly opts in.

### Conflict Resolution UI (Selective merge)
- Show a side-by-side diff of current vs imported values for conflicting keys.
- Allow per-key accept/reject.
- Preview the merged result before applying.

## Non-Functional Requirements

- Export must produce valid JSONC that round-trips through the parser.
- Import validation must complete in under 500ms for typical configs.
- Masking must be applied before any external output (file, clipboard, preview).
- Clipboard integration must work on Windows, macOS, and Linux.

## Acceptance Criteria

- [ ] Export produces valid JSON/JSONC with comments preserved.
- [ ] Secrets masking redacts values matching default patterns.
- [ ] Custom masking patterns are configurable and applied correctly.
- [ ] Import validates against schema and reports errors with field paths.
- [ ] Replace strategy fully replaces the current config.
- [ ] Overlay strategy deep-merges without losing unmentioned keys.
- [ ] Selective strategy shows diff and applies only accepted keys.
- [ ] Clipboard export/import works on all platforms.
- [ ] Unknown top-level keys are rejected by default.
- [ ] Unit tests cover all merge strategies and masking patterns.

## Out of Scope

- Cloud sync or remote config storage.
- Config encryption at rest.
- Import from non-JSON formats (YAML, TOML).

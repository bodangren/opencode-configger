# Track: Schema Validation & Feedback

## Overview

Users can currently save invalid configurations — a wrong type or out-of-range value is only caught when OpenCode itself rejects the file. This track adds real-time, per-field validation that fires as the user edits, showing inline error indicators and blocking save when the config is invalid.

## Functional Requirements

- Each `FieldDef` gains optional `min`, `max`, `required`, `pattern`, and `choices` constraint attributes.
- A `validate_field(field_def, value)` function returns `(is_valid: bool, error_message: str)`.
- Widgets display a red border and tooltip error message when their field is invalid.
- The Save button is disabled (greyed out) while any field is invalid.
- A status bar at the bottom of the window summarises how many errors remain.
- Validation runs on every keystroke / widget change, not only on save.

## Non-Functional Requirements

- Validation must complete in <50 ms per field (no blocking IO).
- Existing valid configs must produce zero validation errors on load.

## Acceptance Criteria

- [ ] `FieldDef` dataclass includes constraint fields (`min`, `max`, `required`, `pattern`, `choices`).
- [ ] `validate_field` is unit-tested for each constraint type, including edge cases.
- [ ] At least one widget per type (text, spinbox, dropdown, checkbox) shows the red-border error state.
- [ ] Save button is disabled when any field is invalid; re-enabled when all errors are resolved.
- [ ] Status bar shows "N error(s)" count that updates in real time.
- [ ] Loading a valid config file produces no validation errors.
- [ ] Test coverage ≥80% for validation logic.

## Out of Scope

- Cross-field validation (e.g., port conflicts between server and MCP).
- Network-based validation against live OpenCode instances.

# Implementation Plan: Schema Validation & Feedback

## Phase 1: Constraint Model

- [x] Task: Extend `FieldDef` with constraint attributes.
  - [x] Add `min`, `max`, `required`, `pattern`, `choices` optional fields to `FieldDef` dataclass in `config_schema.py`.
  - [x] Update all existing `FieldDef` instances to include constraints where applicable (e.g., `port` gets `min=1, max=65535`).
- [x] Task: Implement `validate_field(field_def, value) -> (bool, str)`.
  - [x] Handle each constraint type independently.
  - [x] Return `(True, "")` for valid values; `(False, "<human message>")` for invalid.
- [x] Task: Write unit tests for `validate_field`.
  - [x] One test per constraint type (min, max, required, pattern, choices).
  - [x] Edge cases: None value on required field, value at exact boundary.
- [x] Task: Conductor — User Manual Verification 'Phase 1: Constraint Model' (Protocol in workflow.md)
  [checkpoint: 1c42c3f]

## Phase 2: Widget Error States

- [x] Task: Add error-state display to base widget class in `widgets.py`.
  - [x] `show_error(message)` — applies red border, shows tooltip.
  - [x] `clear_error()` — restores normal border.
  - [x] Wire validation callback into each widget's change event.
- [x] Task: Apply error-state to one widget of each type (text, spinbox, dropdown, checkbox).
- [x] Task: Write widget tests covering error and clear-error transitions.
- [ ] Task: Conductor — User Manual Verification 'Phase 2: Widget Error States' (Protocol in workflow.md)

## Phase 3: Save Guard & Status Bar

- [x] Task: Add status bar to main window showing error count.
  - [x] Status bar updates on every field-change event.
  - [x] Shows "Ready" when no errors; "N error(s) — fix before saving" otherwise.
- [x] Task: Disable Save button while any field is invalid.
  - [x] Maintain an `error_count` counter in app state.
  - [x] Re-enable Save when counter reaches zero.
- [x] Task: Integration test: load a config with a deliberate invalid value and confirm Save is blocked.
- [ ] Task: Conductor — User Manual Verification 'Phase 3: Save Guard & Status Bar' (Protocol in workflow.md)

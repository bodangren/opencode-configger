# Implementation Plan: Enhanced Model Explorer

## Phase 1: Model Loading Backend

- [x] Task: Implement `ModelLoader` (`app/model_loader.py`).
  - [x] Run `opencode models --json` in a background thread with a 10-second timeout.
  - [x] Parse output into `{provider: [ModelInfo(id, name, context_window)]}` dict.
  - [x] On error (not on PATH, timeout), return empty dict and emit an error event.
  - [x] Write unit tests with mocked subprocess output (success, error, timeout cases).
- [ ] Task: Conductor — User Manual Verification 'Phase 1: Model Loading Backend' (Protocol in workflow.md)

## Phase 2: Explorer Widget

- [ ] Task: Rebuild Models tab as `EnhancedModelExplorer` widget (`app/tabs/models.py`).
  - [ ] Provider tree with collapsible sections; each leaf shows model ID, context window, "Set Primary", "Set Small" buttons.
  - [ ] Search box filters visible models in real time (case-insensitive substring match on ID/name).
  - [ ] Provider checkbox strip toggles visibility of individual providers.
  - [ ] "Refresh" button re-invokes `ModelLoader` and redraws tree.
  - [ ] Loading spinner while `ModelLoader` runs.
  - [ ] Error panel with "opencode not found on PATH — check your PATH setting" when load fails.
- [ ] Task: Write widget tests using fixture provider/model data.
  - [ ] Search filters correctly.
  - [ ] Provider toggle hides/shows groups.
  - [ ] Error panel renders on load failure.
- [ ] Task: Conductor — User Manual Verification 'Phase 2: Explorer Widget' (Protocol in workflow.md)

## Phase 3: Set Primary / Set Small Integration

- [ ] Task: Wire "Set Primary" and "Set Small" buttons to update the General tab fields.
  - [ ] Emit a shared event or call a callback that updates `model` / `small_model` FieldDef values in the General tab.
  - [ ] Confirm updated values appear immediately in the General tab without requiring a save.
- [ ] Task: Integration test: select a model, verify General tab fields update.
- [ ] Task: Conductor — User Manual Verification 'Phase 3: Set Primary / Set Small Integration' (Protocol in workflow.md)

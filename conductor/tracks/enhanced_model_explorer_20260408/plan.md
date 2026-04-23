# Implementation Plan: Enhanced Model Explorer

## Phase 1: Model Loading Backend

- [x] Task: Implement `ModelLoader` (`app/model_loader.py`).
  - [x] Run `opencode models --json` in a background thread with a 10-second timeout.
  - [x] Parse output into `{provider: [ModelInfo(id, name, context_window)]}` dict.
  - [x] On error (not on PATH, timeout), return empty dict and emit an error event.
  - [x] Write unit tests with mocked subprocess output (success, error, timeout cases).
- [ ] Task: Conductor — User Manual Verification 'Phase 1: Model Loading Backend' (Protocol in workflow.md)

## Phase 2: Explorer Widget

- [x] Task: Rebuild Models tab as `EnhancedModelExplorer` widget (`app/tabs/models.py`).
  - [x] Provider tree with collapsible sections; each leaf shows model ID, context window, "Set Primary", "Set Small" buttons.
  - [x] Search box filters visible models in real time (case-insensitive substring match on ID/name).
  - [x] Provider checkbox strip toggles visibility of individual providers.
  - [x] "Refresh" button re-invokes `ModelLoader` and redraws tree.
  - [x] Loading spinner while `ModelLoader` runs.
  - [x] Error panel with "opencode not found on PATH — check your PATH setting" when load fails.
- [x] Task: Write widget tests using fixture provider/model data.
  - [x] Search filters correctly.
  - [x] Provider toggle hides/shows groups.
  - [x] Error panel renders on load failure.
- [ ] Task: Conductor — User Manual Verification 'Phase 2: Explorer Widget' (Protocol in workflow.md)

## Phase 3: Set Primary / Set Small Integration

- [x] Task: Wire "Set Primary" and "Set Small" buttons to update the General tab fields.
  - [x] Emit a shared event or call a callback that updates `model` / `small_model` FieldDef values in the General tab.
  - [x] Confirm updated values appear immediately in the General tab without requiring a save.
- [ ] Task: Integration test: select a model, verify General tab fields update.
- [ ] Task: Conductor — User Manual Verification 'Phase 3: Set Primary / Set Small Integration' (Protocol in workflow.md)
# Track: Enhanced Model Explorer

## Overview

The current Model Browser tab lists models from `opencode models` output but provides no search, no provider filtering, and no live refresh. Users working with many providers or custom endpoints struggle to find the right model ID. This track rebuilds the Model Explorer as a searchable, filterable, live-refreshable panel with one-click "Set as primary" / "Set as small model" actions.

## Functional Requirements

- The Models tab shows models grouped by provider in a tree view (provider → model list).
- A search box filters models by name/ID in real time (no button press needed).
- Provider checkboxes allow showing/hiding individual providers.
- A "Refresh" button re-runs `opencode models` and updates the list without restarting.
- Each model row displays: model ID, provider, context window (if available from metadata), and a "Set Primary" / "Set Small" button.
- Clicking "Set Primary" or "Set Small" updates the corresponding field in the General tab immediately.
- If `opencode models` is unavailable (OpenCode not on PATH), a clear error message is shown with a "Configure PATH" hint.

## Non-Functional Requirements

- Search filtering must complete in <100 ms for lists of up to 500 models.
- `opencode models` is called in a background thread to avoid blocking the UI.

## Acceptance Criteria

- [ ] Model list loads on tab open by running `opencode models` in a background thread.
- [ ] Models are grouped under collapsible provider headings.
- [ ] Search box filters the visible list in real time.
- [ ] Provider checkboxes correctly show/hide provider groups.
- [ ] "Refresh" button re-fetches without restarting the app.
- [ ] "Set Primary" updates the `model` field; "Set Small" updates `small_model`.
- [ ] Graceful error state when `opencode` is not on PATH.
- [ ] Coverage ≥80% on model-loading and filtering logic (subprocess mocked in tests).

## Out of Scope

- Favouriting or pinning models persistently.
- Model benchmark data or pricing information.

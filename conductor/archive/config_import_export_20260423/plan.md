# Implementation Plan: Config Import/Export

## Phase 1: Export Module

- [ ] Task: Implement JSON/JSONC export with comment preservation.
  - [ ] Serialize current config to JSONC with original comments intact.
  - [ ] Add export-to-file and export-to-clipboard interfaces.
  - [ ] Write tests for comment round-tripping and file output.
- [ ] Task: Implement secrets masking.
  - [ ] Define default masking patterns (`*API_KEY*`, `*TOKEN*`, `*SECRET*`).
  - [ ] Add user-configurable masking patterns.
  - [ ] Apply masking before any output.
  - [ ] Write tests for default and custom masking patterns.
- [ ] Task: Conductor — User Manual Verification 'Phase 1: Export Module' (Protocol in workflow.md)

## Phase 2: Import and Validation Module

- [ ] Task: Implement import from file and clipboard.
  - [ ] Read JSON/JSONC from file path or clipboard text.
  - [ ] Parse and detect format (JSON vs JSONC).
  - [ ] Write tests for file and clipboard input paths.
- [ ] Task: Implement schema validation for imported configs.
  - [ ] Validate imported config against current schema.
  - [ ] Report errors with field paths and line numbers.
  - [ ] Write tests for valid imports, invalid imports, and unknown keys.
- [ ] Task: Conductor — User Manual Verification 'Phase 2: Import and Validation Module' (Protocol in workflow.md)

## Phase 3: Merge Strategies

- [ ] Task: Implement replace strategy.
  - [ ] Discard current config and apply imported config entirely.
  - [ ] Write tests for full replacement.
- [ ] Task: Implement overlay strategy.
  - [ ] Deep-merge imported config on top of current config.
  - [ ] Imported values win on conflict; unmentioned keys preserved.
  - [ ] Write tests for deep merge behavior.
- [ ] Task: Implement selective strategy.
  - [ ] Compute diff between current and imported configs.
  - [ ] Expose per-key accept/reject API.
  - [ ] Write tests for selective merge with mixed accept/reject.
- [ ] Task: Conductor — User Manual Verification 'Phase 3: Merge Strategies' (Protocol in workflow.md)

## Phase 4: UI Integration

- [ ] Task: Add conflict resolution UI for selective merge.
  - [ ] Show side-by-side diff of current vs imported values.
  - [ ] Allow per-key accept/reject with preview.
  - [ ] Apply only accepted keys on confirm.
- [ ] Task: Add export/import actions to the GUI.
  - [ ] Add Export button with format and masking options.
  - [ ] Add Import button with file picker and clipboard paste.
  - [ ] Show validation errors inline before applying.
- [ ] Task: Write integration tests for export → import round-trip.
  - [ ] Export a config, import it back, verify equivalence.
  - [ ] Test all merge strategies end-to-end.
- [ ] Task: Conductor — User Manual Verification 'Phase 4: UI Integration' (Protocol in workflow.md)

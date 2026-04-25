# Implementation Plan: Configuration Versioning & Migration

## Phase 1: Version Detection

- [ ] Task: Define `SchemaVersion` enum and detection logic (`app/migration.py`).
  - [ ] Add versions: `V1_2`, `V1_3`, `UNKNOWN`.
  - [ ] Implement `detect_version(config_dict) -> SchemaVersion` using structural signals (e.g., `formatter.command` type, presence of `lsp` key).
  - [ ] Write unit tests with fixture dicts for each known version.
- [ ] Task: Measure — User Manual Verification 'Phase 1: Version Detection' (Protocol in workflow.md)

## Phase 2: Migration Registry

- [ ] Task: Implement `MigrationRegistry` with `register` and `migrate` methods.
  - [ ] `register(from_ver, to_ver, fn)` — store migration function.
  - [ ] `migrate(config_dict, from_ver, to_ver) -> config_dict` — apply chain of migrations.
  - [ ] Unknown keys are preserved unchanged.
- [ ] Task: Implement concrete migration: `v1_2_to_v1_3`.
  - [ ] Convert `formatter.command` from string to `[string]` if needed.
  - [ ] Convert `mcp.<name>.command` from string to `[string]` if needed.
- [ ] Task: Write unit tests for migration chain and the v1.2→v1.3 migration with fixtures.
- [ ] Task: Measure — User Manual Verification 'Phase 2: Migration Registry' (Protocol in workflow.md)

## Phase 3: UI Integration & CLI Flag

- [ ] Task: Show migration banner in main window when non-current config is detected on load.
  - [ ] Banner: "Config appears to be from OpenCode vX.Y — click to preview migration."
  - [ ] Clicking opens a diff dialog showing keys that will change.
  - [ ] "Migrate & Save" creates `.bak` backup, writes migrated file, reloads.
- [ ] Task: Add `--migrate <file>` CLI flag to `app/main.py` for headless migration.
  - [ ] Prints migration diff to stdout, writes migrated file, creates `.bak`.
- [ ] Task: Integration tests for banner flow and CLI flag.
- [ ] Task: Measure — User Manual Verification 'Phase 3: UI Integration & CLI Flag' (Protocol in workflow.md)

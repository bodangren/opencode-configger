# Track: Configuration Versioning & Migration

## Overview

OpenCode's config schema changes between releases. Users who upgrade OpenCode find that their existing `opencode.json` may have renamed, removed, or restructured keys. This track adds a versioning layer that detects the schema version of a loaded config file and applies automated migration steps to bring it up to the current schema.

## Functional Requirements

- A `SchemaVersion` enum tracks known OpenCode config versions (e.g., `v1.2`, `v1.3`).
- When loading a config file, `detect_version(config_dict) -> SchemaVersion` infers the version from structural signals (e.g., presence/absence of specific keys).
- A `MigrationRegistry` maps `(from_version, to_version)` pairs to migration functions.
- On load, if the detected version differs from the current version, the app:
  1. Shows a non-blocking banner: "Config appears to be from OpenCode vX.Y — migration available."
  2. Offers a "Migrate & Save" action that applies migrations in sequence and saves.
  3. Shows a diff preview of changes before committing.
- A `--migrate` CLI flag applies migration headlessly without opening the GUI.
- All migrations are lossless: unknown keys are preserved as raw JSON in an "unknown fields" section.

## Non-Functional Requirements

- Migration must produce valid JSONC output.
- Original file is backed up to `<filename>.bak` before writing migrated version.
- Migration functions are independently unit-testable.

## Acceptance Criteria

- [ ] `detect_version` correctly identifies v1.2 vs v1.3 configs from fixture files.
- [ ] At least one concrete migration (v1.2 → v1.3: `command` string → string[]) is implemented and tested.
- [ ] Migration banner appears when a non-current config is loaded.
- [ ] Diff preview shows added/removed/changed keys before save.
- [ ] "Migrate & Save" writes migrated config and creates `.bak` backup.
- [ ] `--migrate <file>` CLI mode works headlessly.
- [ ] Unknown keys are preserved in output.
- [ ] Coverage ≥80% on migration logic.

## Out of Scope

- Downgrade migrations (newer → older schema).
- Cloud-based schema registry.

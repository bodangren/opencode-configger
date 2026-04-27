# Batch Config Operations — Specification

## Overview

Add a batch operations mode that lets users apply templates, validate, import, or export multiple OpenCode config files in a single workflow. Designed for teams that need to standardize configurations across multiple projects or developer machines.

## Problem Statement

Teams using OpenCode often maintain multiple config files (per-project, per-environment, per-developer). The current workflow requires opening and editing each config individually. There is no way to apply a template to a folder of configs, validate multiple configs at once, or export a batch of configs for distribution.

## Functional Requirements

1. **Batch Apply Template** — Select a template and a folder of `opencode.json` files; apply the template to all configs with optional field-level merge strategy (replace, overlay, selective).

2. **Batch Validate** — Select a folder of config files and validate all of them against the schema. Show a summary table: filename, status (valid/invalid), error count, warning count.

3. **Batch Export** — Select the current config and export it to multiple target paths or a zip archive with optional variable substitution per target.

4. **Batch Import** — Import a config into multiple target files, applying merge strategies per file.

5. **Operation Log** — Display a log panel showing each operation's result (file path, status, errors) with timestamps.

6. **Dry Run Mode** — Preview what batch operations would do without writing files. Show before/after summaries.

7. **Progress Indicator** — Show a progress bar for batch operations on large file sets (> 10 files).

8. **Error Recovery** — If one file in a batch fails validation, continue processing remaining files. Report all errors at the end.

## Non-Functional Requirements

- Batch operations run in a background thread to avoid blocking the UI
- Progress reported via callback to update the progress bar
- File I/O uses atomic writes (write to temp, rename) to prevent corruption
- Maximum batch size: 100 files (configurable)

## Out of Scope

- Recursive folder scanning (only top-level folder for v1)
- Batch operations across different config versions (v1.2 vs v1.3)
- Remote file operations (network paths, cloud storage)

## Acceptance Criteria

1. Batch Apply Template applies the selected template to all configs in a folder
2. Batch Validate shows a summary table with per-file status
3. Batch Export creates copies or zip with correct content
4. Dry Run shows what would change without writing
5. Progress bar updates during large batch operations
6. Failed files are skipped; all errors reported at end
7. All existing tests pass

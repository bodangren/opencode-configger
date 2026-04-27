# Implementation Plan — Batch Config Operations

## Phase 1: Batch Data Model & File Discovery

### Tasks

- [ ] **1.1** Write unit tests for `BatchJob` dataclass — file list, operation type, results per file
- [ ] **1.2** Implement `BatchJob` dataclass with `add_file()`, `mark_success()`, `mark_failure()`, `summary()` methods
- [ ] **1.3** Write unit tests for `discover_configs(folder)` — find opencode.json files in top-level folder, handle missing/empty folders
- [ ] **1.4** Implement `discover_configs(folder_path) -> list[Path]` — glob for `opencode.json`, skip directories, return sorted paths

---

## Phase 2: Batch Validate

### Tasks

- [ ] **2.1** Write unit tests for `batch_validate()` — validates multiple files, collects errors per file
- [ ] **2.2** Implement `batch_validate(file_paths) -> BatchJob` — load each file, run schema validation, record results
- [ ] **2.3** Write unit tests for `BatchValidateDialog` — summary table rendering, error detail view
- [ ] **2.4** Implement `BatchValidateDialog` (ttk.Toplevel) — table with columns: filename, status, errors, warnings

---

## Phase 3: Batch Apply Template

### Tasks

- [ ] **3.1** Write unit tests for `batch_apply_template()` — applies template to multiple configs with merge strategy
- [ ] **3.2** Implement `batch_apply_template(template, file_paths, strategy) -> BatchJob` — load config, merge template, record result
- [ ] **3.3** Write unit tests for `BatchApplyDialog` — file selection, template picker, strategy selector, dry run preview
- [ ] **3.4** Implement `BatchApplyDialog` — template dropdown, strategy radio buttons (replace/overlay/selective), dry run checkbox

---

## Phase 4: Batch Export & Dry Run

### Tasks

- [ ] **4.1** Write unit tests for `batch_export()` — copy config to multiple targets or zip archive
- [ ] **4.2** Implement `batch_export(source, targets, as_zip) -> BatchJob` — atomic write to each target path
- [ ] **4.3** Write unit tests for `dry_run_preview()` — simulate operation without writing, return change summary
- [ ] **4.4** Implement `dry_run_preview()` — returns list of (file, action, diff_summary) tuples

---

## Phase 5: Progress & Operation Log

### Tasks

- [ ] **5.1** Write unit tests for `BatchProgressDialog` — progress bar update, cancel support
- [ ] **5.2** Implement `BatchProgressDialog` — ttk.Progressbar, file count label, cancel button
- [ ] **5.3** Implement `OperationLog` panel — scrollable text widget showing timestamped operation results
- [ ] **5.4** Wire batch operations to background thread with progress callback

---

## Phase 6: Integration & Polish

### Tasks

- [ ] **6.1** Add "Batch Operations" menu item to main window menu bar
- [ ] **6.2** Wire batch validate/apply/export to menu items
- [ ] **6.3** Run full test suite — verify no regressions
- [ ] **6.4** Update `measure/tech-debt.md` — note any new debt items

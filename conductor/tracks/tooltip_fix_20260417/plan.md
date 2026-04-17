# Plan: Tooltip Fix Track

## Phase 1: Fix ToolTip to support text update
- [x] Add `set_text()` method to `ToolTip` class that updates label text if tip_window exists
- [x] Add `show()` method to explicitly show the tooltip

## Phase 2: Fix LabeledEntry.show_error
- [x] Change to reuse existing _error_tooltip instead of creating new
- [x] Test: call show_error twice, verify only one tooltip instance

## Phase 3: Fix LabeledCombo.show_error
- [x] Same pattern as LabeledEntry

## Phase 4: Fix LabeledCheck.show_error
- [x] Same pattern (note: no error frame highlight for checkboxes)

## Phase 5: Fix LabeledSpinbox.show_error
- [x] Same pattern as LabeledEntry

## Phase 6: Run full test suite
- [x] pytest tests/ — 64 passed, 47 skipped (GUI tests need display)
- [x] Module imports OK
# Widget-Wired Undo/Redo — Implementation Plan

## Phase 1: Audit Widget Changes [ ]
- [ ] List all editable widgets in the GUI
- [ ] Identify which widgets already have change handlers
- [ ] Map widget types to `record_change()` call patterns

## Phase 2: Wire Change Tracking [ ]
- [ ] Add `record_change()` calls to text entry widgets
- [ ] Add `record_change()` calls to dropdown/combobox widgets
- [ ] Add `record_change()` calls to checkbox/radio widgets
- [ ] Test undo/redo for each widget type

## Phase 3: Persistence [ ]
- [ ] Implement history serialization to disk
- [ ] Load history on application start
- [ ] Add history size limit (e.g., 100 changes)

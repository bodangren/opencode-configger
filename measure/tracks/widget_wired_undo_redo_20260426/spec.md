# Widget-Wired Undo/Redo

## Problem
`record_change()` is available but not wired to editable widgets, so undo/redo doesn't track actual user changes.

## Solution
Connect `record_change()` to all editable widgets (text fields, dropdowns, checkboxes) for full change tracking.

## Acceptance Criteria
- [ ] All editable widgets call `record_change()` on value change
- [ ] Undo reverts last widget change
- [ ] Redo re-applies reverted change
- [ ] History persists across sessions

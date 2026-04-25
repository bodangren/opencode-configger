# Track: Tooltip Fix — Error tooltip re-show bug

## Problem
Error tooltip re-shows on every `show_error` call because:
1. `show_error` calls `_hide` on old tooltip then creates a new ToolTip
2. Old tooltip's event bindings (`<Enter>`, `<Leave>`) remain on the widget
3. When mouse enters widget, old tooltip's `_show` fires (tip_window is None from _hide)
4. Old tooltip creates a new tip_window, causing duplicate/rogue tooltips

## Solution
Reuse a single `ToolTip` instance for error display. Instead of:
```
_hide(old) → create new ToolTip
```
Use:
```
if existing: update text, call _show
else: create once, store in _error_tooltip
```

## Affected Widgets
- LabeledEntry.show_error (line 81)
- LabeledCombo.show_error (line 133)
- LabeledCheck.show_error (line 257)
- LabeledSpinbox.show_error (line 519)

## Verification
Manual test: trigger validation error, trigger again, verify no duplicate tooltips on hover
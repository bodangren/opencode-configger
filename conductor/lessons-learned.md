# Lessons Learned

> This file is curated working memory, not an append-only log. Keep it at or below **50 lines**.
> Remove or condense entries that are no longer relevant to near-term planning.

## Architecture & Design
<!-- Decisions made that future tracks should be aware of -->

## Recurring Gotchas
<!-- Problems encountered repeatedly; save future tracks from the same pain -->

## Patterns That Worked Well
<!-- Approaches worth repeating -->
- `validate_field` + `validate_config` pattern: field-level validators composed into a full-config validator — easy to test in isolation and extend per section.
- Error border via tk.Frame `highlightbackground` + `highlightthickness` — cleaner than ttk styling for dynamic error states.

## Implementation Notes
<!-- Notes about constraint fields naming -->
- Plan spec uses `min`/`max`/`choices` but implementation uses `min_value`/`max_value`/`enum_values` — semantics are identical, just naming difference. No refactoring needed.
- Widget error state uses wrapper tk.Frame with red highlightborder around the inner ttk widget.

## Planning Improvements
<!-- Notes on where estimates were wrong and why -->
- Phase 6 (Polish) tasks were smaller than Phase 1-5 (Schema + Widgets) — 4 tasks completed in one session vs multi-session phases earlier.
- Phase 6.1-6.3 (validation, status bar, variable preview) were already implemented before Phase 6 started — plan was ahead of marks.
- Phase 2 (Widget Error States): 4 tasks completed in one session — show_error/clear_error pattern is consistent across widget types.

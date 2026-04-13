# Tech Debt Registry

> This file is curated working memory, not an append-only log. Keep it at or below **50 lines**.
> Remove or summarize resolved items when they no longer need to influence near-term planning.
>
> **Severity:** `Critical` | `High` | `Medium` | `Low`
> **Status:** `Open` | `Resolved`

| Date | Track | Item | Severity | Status | Notes |
|------|-------|------|----------|--------|-------|
| 2026-04-12 | Schema Validation | Error tooltip re-shows on every show_error call | Low | Open | ToolTip._hide is called but tooltip instance persists; acceptable for MVP |
| 2026-04-13 | Schema Validation Phase 3 | Status bar error label placeholder — no entry widget to wire per-field validation directly | Low | Open | Validation is full-config only; per-field inline errors not yet wired to status bar |



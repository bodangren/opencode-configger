# Tech Debt Registry

> This file is curated working memory, not an append-only log. Keep it at or below **50 lines**.
> Remove or summarize resolved items when they no longer need to influence near-term planning.
>
> **Severity:** `Critical` | `High` | `Medium` | `Low`
> **Status:** `Open` | `Resolved`

| Date | Track | Item | Severity | Status | Notes |
|------|-------|------|----------|--------|-------|
| 2026-04-13 | Schema Validation Phase 3 | Status bar error label placeholder — no entry widget to wire per-field validation directly | Low | Open | Validation is full-config only; per-field inline errors not yet wired to status bar |
| 2026-04-23 | Config Import/Export | SecretsMasker uses simple substring match instead of regex for patterns | Low | Open | _contains_secret does case-insensitive substring check; default patterns are keyword-based (API_KEY, TOKEN, etc.) |
| 2026-04-24 | Config Versioning | detect_version() defaults to V1_3 — a config with no formatter/mcp section is assumed v1.3, which may misidentify future older configs | Low | Open | Only two versions exist today; may need explicit version field |
| 2026-04-24 | Model Explorer | clipboard code in config_export.py creates tk.Tk() root for each clipboard op — risks conflicts with existing root in GUI mode | Medium | Open | Could accept an optional root parameter or use a shared clipboard utility |
| 2026-04-24 | Architecture Graph | GraphCanvas pan/zoom rescale implementation is basic — scrollregion resize on zoom may be imperfect | Low | Open | Works for moderate zoom levels; complex configs may need canvas size adaption |
| 2026-04-24 | Config Templates | TemplateRepository custom templates stored in ~/.configger/templates — not backed up with config | Low | Open | Custom templates persist across sessions but not with the config file |



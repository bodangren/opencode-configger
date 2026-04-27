# Implementation Plan — Config Search & Quick-Jump

## Phase 1: Search Index & Data Model

### Tasks

- [ ] **1.1** Write unit tests for `SearchIndex` — build index from schema, lookup by key path, label, and value
- [ ] **1.2** Implement `SearchIndex` class: `build_from_schema()`, `search(query)`, `get_entry(key_path)`
- [ ] **1.3** Write unit tests for `SearchResult` dataclass — relevance scoring, match type (exact/prefix/substring)
- [ ] **1.4** Implement `SearchResult` dataclass with relevance ranking logic

---

## Phase 2: Search Bar Widget

### Tasks

- [ ] **2.1** Write unit tests for `SearchBar` widget — input, dropdown display, result selection
- [ ] **2.2** Implement `SearchBar` class (ttk.Frame) with entry input, results dropdown (Toplevel), and keyboard bindings
- [ ] **2.3** Implement real-time filtering — debounce 150ms, update dropdown on each keystroke
- [ ] **2.4** Implement keyboard navigation — Up/Down arrows, Enter to select, Escape to close

---

## Phase 3: Quick-Jump & Widget Highlighting

### Tasks

- [ ] **3.1** Write unit tests for `quick_jump()` — switches tab, focuses widget, triggers highlight
- [ ] **3.2** Implement `quick_jump(key_path)` on main app — locate tab and widget from index, call `notebook.select()` and `widget.focus_set()`
- [ ] **3.3** Implement widget highlight flash — temporary background color change (300ms) on jumped-to widget
- [ ] **3.4** Write integration test — search for a key, verify tab switched and widget focused

---

## Phase 4: Search Index Integration & Keyboard Shortcuts

### Tasks

- [ ] **4.1** Wire `SearchIndex.build_from_schema()` to main app config load — rebuild on `_load_config()`
- [ ] **4.2** Add `Ctrl+F` and `/` global keyboard shortcuts to focus search bar
- [ ] **4.3** Implement recent searches — store last 5 queries in session, show on search bar focus
- [ ] **4.4** Add empty/no-results state label in dropdown

---

## Phase 5: Polish & Integration

### Tasks

- [ ] **5.1** Run full test suite — verify no regressions
- [ ] **5.2** Performance test — verify search < 50ms on a config with 500+ keys
- [ ] **5.3** Update `measure/tech-debt.md` — mark Undo/Redo record_change wiring as resolved if applicable

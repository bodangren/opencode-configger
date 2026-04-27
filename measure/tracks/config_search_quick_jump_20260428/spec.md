# Config Search & Quick-Jump — Specification

## Overview

Add a global search bar that lets users find any config key, value, or setting across all tabs and jump directly to the matching widget. With 87+ keybind slots, dozens of provider/agent/tool config keys, and deeply nested MCP server settings, users currently have to hunt through tabs manually. Search provides instant access to any setting.

## Problem Statement

The OpenCode config schema has hundreds of editable fields spread across 15+ tabs. Users frequently know *what* they want to change but not *where* it lives in the tab hierarchy. There is no way to search for a setting by name, key path, or value without clicking through every tab.

## Functional Requirements

1. **Global Search Bar** — A persistent search input in the main window toolbar (always visible, `Ctrl+F` or `/` to focus).

2. **Search Index** — A pre-built index mapping every editable config key path (e.g., `agent.build.model`, `provider.openai.apiKey`, `tui.keybinds.submit`) to its tab, widget reference, and display label.

3. **Real-Time Filtering** — As the user types, a dropdown results list updates instantly showing matching keys, values, and labels. Results are ranked by relevance (exact match > prefix > substring).

4. **Quick-Jump on Selection** — Selecting a result (Enter or click) switches to the target tab and focuses the matching widget, optionally highlighting it with a brief flash animation.

5. **Search Scope** — Search covers:
   - Config key paths (dot-notation)
   - Display labels (human-readable names)
   - Current values (find which agent uses a specific model)
   - Keybind descriptions (find which action maps to Ctrl+Shift+Z)

6. **Keyboard Navigation** — Arrow keys navigate results, Enter selects, Escape closes the dropdown. Fully keyboard-driven workflow.

7. **Recent Searches** — Persist the last 5 searches in session memory for quick re-access.

8. **Empty/No-Results State** — Show "No matching settings" with a suggestion to check spelling or broaden the search.

## Non-Functional Requirements

- Search index built once on config load, rebuilt on schema change
- Results filtered in < 50ms for configs with 500+ keys
- No blocking I/O on main thread
- Pure tkinter implementation (no external search libraries)

## Out of Scope

- Regex or fuzzy search (plain substring for v1)
- Search across multiple config files simultaneously
- Editing search results inline (jump only, edit in place)

## Acceptance Criteria

1. `Ctrl+F` or `/` focuses the search bar from anywhere in the app
2. Typing filters results in real-time from a pre-built index
3. Selecting a result navigates to the correct tab and focuses the widget
4. Search covers key paths, labels, values, and keybind descriptions
5. Keyboard navigation works (arrows, Enter, Escape)
6. All existing tests pass

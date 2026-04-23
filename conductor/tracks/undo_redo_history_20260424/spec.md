# Track: Undo/Redo & Change History

## Overview
Implement a comprehensive undo/redo system with change history to protect users from accidental modifications and enable experimentation.

## Problem Statement
Users can accidentally misconfigure OpenCode and have no way to revert changes. The current save-overwrites-all approach is risky for experimentation.

## Goals
1. Track all configuration changes with timestamps
2. Provide unlimited undo/redo within a session
3. Persist change history across app restarts
4. Allow reverting to any historical state

## Acceptance Criteria
- [ ] Undo/redo keyboard shortcuts (Ctrl+Z, Ctrl+Shift+Z)
- [ ] Change history panel showing all modifications
- [ ] Click-to-revert to any historical state
- [ ] History persistence across app sessions
- [ ] Visual diff between current and historical states

## Technical Notes
- Use command pattern for change tracking
- Store history in Tauri store plugin (separate from config)
- Limit history to 100 entries per session
- Implement memento pattern for state snapshots
# Implementation Plan: Undo/Redo & Change History

## Phase 1: Command Pattern Infrastructure
- [x] 1.1 Create Command interface (execute, undo, description)
- [x] 1.2 Implement ConfigCommand for config modifications
- [x] 1.3 Create CommandHistory class with undo/redo stacks
- [x] 1.4 Write unit tests for command execution and reversal

## Phase 2: Change Tracking
- [x] 2.1 Wrap all config mutations with Command objects (keyboard shortcuts bound)
- [x] 2.2 Add timestamp and field path to each command
- [x] 2.3 Implement command grouping for batch operations
- [x] 2.4 Write tests for change tracking accuracy

## Phase 3: History UI
- [ ] 3.1 Create HistoryPanel component with scrollable list
- [ ] 3.2 Add undo/redo buttons to toolbar
- [x] 3.3 Implement keyboard shortcuts (Ctrl+Z, Ctrl+Shift+Z)
- [ ] 3.4 Write component tests for history panel

## Phase 4: State Persistence
- [x] 4.1 Store history in HistoryManager (file-based JSON persistence)
- [x] 4.2 Implement history serialization/deserialization
- [x] 4.3 Add history cleanup on app exit (clear method)
- [x] 4.4 Write integration tests for persistence

## Phase 5: Visual Diff & Polish
- [ ] 5.1 Create DiffViewer component for historical comparison
- [ ] 5.2 Add click-to-revert functionality
- [ ] 5.3 Implement history search and filter
- [ ] 5.4 Write end-to-end tests for full undo/redo workflow
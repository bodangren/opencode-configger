# Implementation Plan: Config Diff & Merge Tool

## Phase 1: Diff Engine
- [x] 1.1 Create DiffEngine with field-level comparison
- [x] 1.2 Implement change classification (added, removed, modified, conflict)
- [x] 1.3 Add diff serialization to JSON format
- [x] 1.4 Write unit tests for diff accuracy

## Phase 2: Diff Viewer UI
- [ ] 2.1 Create DiffViewer component with side-by-side layout
- [ ] 2.2 Add color-coded change indicators (green=added, red=removed, yellow=modified)
- [ ] 2.3 Implement collapsible sections for nested objects
- [ ] 2.4 Write component tests for diff rendering

## Phase 3: Three-Way Merge
- [ ] 3.1 Create MergeResolver for conflict resolution
- [ ] 3.2 Add merge strategy selector (keep ours, keep theirs, custom)
- [ ] 3.3 Implement conflict preview with resolution options
- [ ] 3.4 Write tests for merge resolution logic

## Phase 4: Integration with Import Flow
- [ ] 4.1 Replace current merge dialog with DiffViewer
- [ ] 4.2 Add merge preview before applying changes
- [ ] 4.3 Implement undo merge functionality
- [ ] 4.4 Write integration tests for import-diff-merge flow

## Phase 5: Export & Reporting
- [ ] 5.1 Add diff export as JSON report
- [ ] 5.2 Create human-readable diff summary
- [ ] 5.3 Implement diff history tracking
- [ ] 5.4 Write end-to-end tests for diff export
# Track: Config Diff & Merge Tool

## Overview
Visual diff and merge tool for comparing configuration files, enabling users to understand changes and merge configurations from different sources.

## Problem Statement
When importing configs or comparing versions, users need to see exactly what changed. The existing import flow shows conflicts but lacks a visual diff view.

## Goals
1. Side-by-side config comparison with highlighting
2. Three-way merge for conflict resolution
3. Field-level change tracking
4. Merge preview before applying

## Acceptance Criteria
- [ ] Side-by-side diff view with added/removed/modified highlighting
- [ ] Three-way merge for import conflicts
- [ ] Field-level change indicators
- [ ] Merge preview with conflict resolution
- [ ] Export diff as report

## Technical Notes
- Extend existing compute_diff from config_import.py
- Use difflib for text-based diff generation
- Add DiffViewer tab to import workflow
- Support both JSON and JSONC formats
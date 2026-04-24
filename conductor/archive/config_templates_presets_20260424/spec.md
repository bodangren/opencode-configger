# Track: Config Templates & Presets

## Overview
Provide pre-built configuration templates for common OpenCode setups, enabling users to quickly bootstrap their configuration for different use cases.

## Problem Statement
New users face a blank config with dozens of options. Creating a working configuration from scratch requires reading documentation and understanding OpenCode's schema. Templates reduce onboarding friction.

## Goals
1. Ship 5+ built-in templates for common setups (Python dev, full-stack, data science, etc.)
2. Allow users to save custom configurations as templates
3. Provide template preview before applying
4. Support template merging with existing config

## Acceptance Criteria
- [ ] Built-in template library with 5+ configurations
- [ ] Template browser UI with search and preview
- [ ] One-click template application
- [ ] Custom template save/export functionality
- [ ] Template merge strategy (replace, overlay, selective)

## Technical Notes
- Store templates as JSONC files in app/templates/
- Use existing merge strategies from config_import.py
- Template schema validates against config_schema.py
- Add Templates tab to main navigation
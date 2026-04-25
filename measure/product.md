# Product Definition

## Product Name
OpenCode Configger

## Vision
A desktop GUI utility that makes configuring OpenCode painless. Instead of hand-editing JSON files and memorizing schema keys, users get a form-based interface with validation, defaults, and documentation inline.

## Target Users
- Developers who use OpenCode as their AI coding assistant
- Users who want to customize providers, models, agents, keybindings, and TUI settings without reading docs
- Teams that need to share standardized OpenCode configurations

## Core Features

### 1. Main Config Editor (`opencode.json`)
- Edit all top-level config keys: model, small_model, default_agent, logLevel, share, autoupdate, snapshot, username
- Provider configuration with custom provider support (npm package, baseURL, models)
- Agent configuration (model, prompt, tools, description, mode, color, steps, permissions)
- Server settings (port, hostname, mDNS, CORS)
- Tool permissions (read, edit, bash, glob, grep — allow/ask/deny per tool)
- MCP server configuration (stdio, SSE, streamable-http)
- Command definitions (template, description, agent, model)
- Formatter configuration (command, extensions, environment, disabled)
- Watcher ignore patterns
- Plugin list
- Instructions paths
- Compaction settings (auto, prune, reserved)
- Provider enable/disable lists

### 2. TUI Config Editor (`tui.json`)
- Theme selection
- Keybinding editor with all 87+ keybind slots
- Scroll speed and acceleration
- Diff style (auto/stacked)

### 3. Config File Management
- Load from any of the standard config locations
- Save with proper JSONC formatting
- Create new config files
- Variable substitution preview ({env:VAR}, {file:path})

### 4. Model Browser
- Display available models grouped by provider (from `opencode-cli models`)
- Quick-set model as primary or small model

## Non-Functional Requirements
- Single-file or minimal-dependency Python application
- Cross-platform (Linux, macOS, Windows)
- No external services required
- Config validation against known schema before save

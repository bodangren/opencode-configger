# Interactive Architecture Graph — Specification

## Overview

Add a visual tab that renders a directed graph of the configured agents, providers, tools, commands, formatters, MCP servers, and LSP servers to help users visualize their OpenCode setup at a glance.

## Functional Requirements

1. **New "Architecture" Tab** — A notebook tab that renders an interactive node-link diagram of the full configuration.

2. **Node Types** — Each configurable entity type is a distinct node category:
   - **Model/Provider** nodes (e.g., openai, anthropic)
   - **Agent** nodes (e.g., build, plan, general)
   - **Tool/Permission** nodes (e.g., bash, read, edit)
   - **Command** nodes
   - **Formatter** nodes
   - **MCP Server** nodes
   - **LSP Server** nodes

3. **Edge Types (Directed Relationships)**:
   - Agent → Provider (agent's `model` references a provider)
   - Agent → Tool (agent has permission to use a tool)
   - Command → Agent (command uses a specific agent)
   - Formatter → (no outbound edges — terminal node)
   - MCP Server → (terminal — external service)
   - LSP Server → (terminal — external service)

4. **Graph Layout** — Hierarchical left-to-right layout (providers/agents on left, tools/terminal nodes on right), computed via a simple layered layout algorithm.

5. **Node Display** — Each node shows its name and a small type icon/label. Nodes are color-coded by category.

6. **Interactive Features**:
   - Click a node to highlight its connections (neighbors)
   - Hover tooltip showing full config path (e.g., `agent.build.model`)
   - Pan canvas by dragging
   - Zoom with mousewheel

7. **Live Sync** — When the user switches to the Architecture tab, the graph refreshes from current tab data. The graph does not edit the config — it is read-only visualization.

8. **Empty State** — If a section has no entries, show a placeholder node labeled "(none)" for that category.

## Non-Functional Requirements

- Pure tkinter Canvas-based rendering (no external graph libraries)
- Responsive layout within tab bounds
- No blocking I/O on the main thread

## Out of Scope

- Editing configuration from the graph (read-only visualization)
- Exporting the graph as an image
- Animated transitions between layouts

## Acceptance Criteria

1. A new "Architecture" tab appears in the notebook after Extensions
2. Loading a config renders a directed graph with correctly categorized nodes
3. Edges correctly represent agent→provider and agent→tool relationships
4. Clicking a node highlights its direct neighbors
5. Pan and zoom work smoothly
6. All existing tests pass
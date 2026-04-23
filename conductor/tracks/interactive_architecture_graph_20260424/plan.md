# Implementation Plan — Interactive Architecture Graph

## Phase 1: Graph Data Model & Layout Engine

### Tasks

- [ ] **1.1** Write unit tests for `GraphData` model (nodes, edges, adjacency)
- [ ] **1.2** Implement `GraphData` class: `add_node()`, `add_edge()`, `get_neighbors()`
- [ ] **1.3** Write unit tests for `HierarchicalLayout` (layer assignment, x/y computation)
- [ ] **1.4** Implement `HierarchicalLayout` — assigns layers left-to-right, computes node positions

---

## Phase 2: Architecture Tab — Canvas Rendering

### Tasks

- [ ] **2.1** Write unit tests for `ArchitectureTab` node rendering (color, size, label)
- [ ] **2.2** Implement `ArchitectureTab` class inheriting from `ttk.Frame`
- [ ] **2.3** Implement `GraphCanvas` widget using `tk.Canvas` for node/edge drawing
- [ ] **2.4** Implement `draw_node()` — colored rounded rectangle with label
- [ ] **2.5** Implement `draw_edge()` — directed arrow between nodes
- [ ] **2.6** Implement `redraw()` — clears canvas and redraws all nodes/edges

---

## Phase 3: Graph Construction from Config Data

### Tasks

- [ ] **3.1** Write unit tests for `build_graph_from_config()` — extracts nodes and edges from config dict
- [ ] **3.2** Implement `build_graph_from_config()` — traverses `agent`, `provider`, `permission`, `command`, `formatter`, `mcp`, `lsp` sections
- [ ] **3.3** Wire `ArchitectureTab.load_graph()` to receive config data from main app
- [ ] **3.4** Implement node type color mapping (provider=blue, agent=green, tool=orange, etc.)

---

## Phase 4: Interactive Features (Highlight, Pan, Zoom)

### Tasks

- [ ] **4.1** Write unit tests for `highlight_neighbors()` — click detection and neighbor highlighting
- [ ] **4.2** Implement node click handler — highlights direct neighbors with accent color
- [ ] **4.3** Implement hover tooltip — shows full config path on mouseover
- [ ] **4.4** Implement pan — drag canvas to pan view
- [ ] **4.5** Implement zoom — mousewheel zoom in/out (scale transform)

---

## Phase 5: Integration — Main App Wiring

### Tasks

- [ ] **5.1** Register `ArchitectureTab` in `main.py` (`_build_tabs()` and `_build_tab_order`)
- [ ] **5.2** Wire `_collect_from_tabs()` to gather data for graph (read-only pass)
- [ ] **5.3** Add Architecture tab after Extensions tab in notebook
- [ ] **5.4** Run full test suite — verify no regressions

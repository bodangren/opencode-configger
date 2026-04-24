"""Architecture tab — interactive graph visualization of OpenCode config."""

import tkinter as tk
from tkinter import ttk
from typing import Any

from app.architecture_graph import (
    GraphData,
    GraphNode,
    HierarchicalLayout,
    NODE_COLORS,
    NodeType,
    node_color,
)


class GraphCanvas:
    def __init__(
        self,
        canvas: tk.Canvas,
        node_width: float = 80.0,
        node_height: float = 40.0,
    ) -> None:
        self.canvas = canvas
        self.node_width = node_width
        self.node_height = node_height
        self._node_items: dict[str, int] = {}
        self._edge_items: list[int] = []
        self._scale: float = 1.0
        self._offset_x: float = 0.0
        self._offset_y: float = 0.0
        self._graph: GraphData | None = None
        self._highlighted_neighbors: set[str] = set()
        self._tooltip: tk.Toplevel | None = None

    def _screen_to_graph(self, sx: float, sy: float) -> tuple[float, float]:
        return (sx - self._offset_x) / self._scale, (sy - self._offset_y) / self._scale

    def _find_node_at(self, x: float, y: float) -> str | None:
        if self._graph is None:
            return None
        for node_id, node in self._graph.nodes.items():
            nx = node.x
            ny = node.y
            if nx <= x <= nx + self.node_width and ny <= y <= ny + self.node_height:
                return node_id
        return None

    def highlight_neighbors(self, node_id: str, neighbors: list[str]) -> None:
        self._highlighted_neighbors = set(neighbors + [node_id])
        for nid, item in self._node_items.items():
            fill = self.canvas.itemcget(item, "fill")
            outline = self.canvas.itemcget(item, "outline")
            if nid in self._highlighted_neighbors and nid != node_id:
                self.canvas.itemconfig(item, fill="#ffcc00", outline="#ff9900", width=2.5)
            elif nid == node_id:
                self.canvas.itemconfig(item, fill="#ffffff", outline="#333333", width=3)
            else:
                orig_color = node_color(self._graph.nodes[nid].node_type)
                self.canvas.itemconfig(item, fill=orig_color, outline="#333333", width=1.5)

    def clear_highlight(self) -> None:
        if self._graph is None:
            return
        for nid, item in self._node_items.items():
            orig_color = node_color(self._graph.nodes[nid].node_type)
            self.canvas.itemconfig(item, fill=orig_color, outline="#333333", width=1.5)
        self._highlighted_neighbors.clear()

    def show_tooltip(self, node_id: str, screen_x: int, screen_y: int) -> None:
        if self._graph is None or node_id not in self._graph.nodes:
            return
        node = self._graph.nodes[node_id]
        path = self._config_path_for_node(node)
        if self._tooltip is None:
            self._tooltip = tk.Toplevel(self.canvas)
            self._tooltip.withdraw()
            self._tooltip.overrideredirect(True)
            self._tooltip_label = ttk.Label(self._tooltip, text="", background="#ffffcc",
                                           relief="solid", padding=(4, 2))
            self._tooltip_label.pack()
        self._tooltip_label.config(text=path)
        self._tooltip.geometry(f"+{screen_x + 12}+{screen_y + 12}")
        self._tooltip.deiconify()

    def hide_tooltip(self) -> None:
        if self._tooltip is not None:
            self._tooltip.withdraw()

    def set_scale(self, scale: float) -> None:
        self._scale = max(0.2, min(3.0, scale))

    def get_scale(self) -> float:
        return self._scale

    def set_offset(self, dx: float, dy: float) -> None:
        self._offset_x = dx
        self._offset_y = dy

    def get_offset(self) -> tuple[float, float]:
        return self._offset_x, self._offset_y

    def draw_node(self, node: GraphNode) -> str | None:
        node_id = node.node_id
        color = node_color(node.node_type)
        x = node.x + self._offset_x
        y = node.y + self._offset_y
        w = self.node_width
        h = self.node_height

        cx = x + w / 2
        cy = y + h / 2
        r = min(w, h) / 4

        oval = self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=color,
            outline="#333333",
            width=1.5,
            tags=(f"node_{node_id}", "node"),
        )

        label_text = node.data.get("label", node_id)
        label = self.canvas.create_text(
            cx, cy + r + 14,
            text=label_text,
            fill="#222222",
            font=("TkDefaultFont", 9),
            tags=(f"node_{node_id}", "node_label", "label"),
        )

        self._node_items[node_id] = oval
        return node_id

    def _config_path_for_node(self, node: GraphNode) -> str:
        nid = node.node_id
        if nid.startswith("provider:"):
            return f"provider.{nid.split(':', 1)[1]}"
        elif nid.startswith("agent:"):
            return f"agent.{nid.split(':', 1)[1]}"
        elif nid.startswith("tool:"):
            return f"permission.{nid.split(':', 1)[1]}"
        elif nid.startswith("command:"):
            return f"command.{nid.split(':', 1)[1]}"
        elif nid.startswith("formatter:"):
            return f"formatter.{nid.split(':', 1)[1]}"
        elif nid.startswith("mcp:"):
            return f"mcp.{nid.split(':', 1)[1]}"
        elif nid.startswith("lsp:"):
            return f"lsp.{nid.split(':', 1)[1]}"
        return nid

    def draw_edge(self, source: GraphNode, target: GraphNode, edges: set) -> int | None:
        sx = source.x + self._offset_x + self.node_width / 2
        sy = source.y + self._offset_y + self.node_height / 2
        tx = target.x + self._offset_x + self.node_width / 2
        ty = target.y + self._offset_y + self.node_height / 2

        line = self.canvas.create_line(
            sx, sy, tx, ty,
            fill="#666666",
            width=1.5,
            arrow=tk.LAST,
            tags=("edge", "edge_line"),
        )
        self._edge_items.append(line)
        return line

    def clear(self) -> None:
        self.canvas.delete("node")
        self.canvas.delete("edge")
        self.canvas.delete("node_label")
        self._node_items.clear()
        self._edge_items.clear()

    def redraw(self, graph: GraphData) -> None:
        self.clear()
        layout = HierarchicalLayout(graph)
        layout.compute()

        for edge in graph.edges:
            src, tgt = edge
            if src in graph.nodes and tgt in graph.nodes:
                self.draw_edge(graph.nodes[src], graph.nodes[tgt], graph.edges)

        for node in graph.nodes.values():
            self.draw_node(node)


class ArchitectureTab(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        on_change: Any = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self._current_graph: GraphData | None = None

        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        ttk.Label(
            header, text="Architecture", font=("TkDefaultFont", 12, "bold")
        ).pack(side=tk.LEFT)
        self.hint_label = ttk.Label(
            header,
            text="Click a node to highlight connections. Scroll to zoom.",
            font=("TkDefaultFont", 8),
            foreground="#888",
        )
        self.hint_label.pack(side=tk.RIGHT, padx=(0, 8))

        canvas = tk.Canvas(self, highlightthickness=0, background="#fafafa")
        hbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        vbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(
            xscrollcommand=hbar.set,
            yscrollcommand=vbar,
            scrollregion=(0, 0, 1200, 800),
        )

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.graph_canvas = GraphCanvas(canvas)

        canvas.bind("<MouseWheel>", self._on_mousewheel)
        canvas.bind("<Button-2>", self._on_pan_start)
        canvas.bind("<B2-Motion>", self._on_pan)
        canvas.bind("<Button-1>", self._on_click)
        canvas.bind("<Motion>", self._on_hover)

    def load_graph(self, graph: GraphData) -> None:
        self._current_graph = graph
        self.graph_canvas._graph = graph
        self.graph_canvas.redraw(graph)

    def load_config(self, data: dict) -> None:
        graph = _build_graph_from_config(data)
        self.load_graph(graph)

    def save_config(self, data: dict) -> None:
        pass

    def _on_mousewheel(self, event: tk.Event) -> None:
        delta = event.delta
        scale = self.graph_canvas.get_scale()
        new_scale = scale * (1.0 + delta / 1200.0)
        self.graph_canvas.set_scale(new_scale)
        self._rescale_canvas()

    def _on_pan_start(self, event: tk.Event) -> None:
        self._pan_start_x = event.x
        self._pan_start_y = event.y
        self._pan_start_offset = self.graph_canvas.get_offset()

    def _on_pan(self, event: tk.Event) -> None:
        dx = event.x - self._pan_start_x
        dy = event.y - self._pan_start_y
        ox, oy = self._pan_start_offset
        self.graph_canvas.set_offset(ox + dx, oy + dy)
        self._rescale_canvas()

    def _on_click(self, event: tk.Event) -> None:
        if self._current_graph is None:
            return
        gx, gy = self.graph_canvas._screen_to_graph(event.x, event.y)
        node_id = self.graph_canvas._find_node_at(gx, gy)
        if node_id:
            neighbors = self._current_graph.get_neighbors(node_id)
            self.graph_canvas.highlight_neighbors(node_id, neighbors)
        else:
            self.graph_canvas.clear_highlight()

    def _on_hover(self, event: tk.Event) -> None:
        if self._current_graph is None:
            return
        gx, gy = self.graph_canvas._screen_to_graph(event.x, event.y)
        node_id = self.graph_canvas._find_node_at(gx, gy)
        if node_id:
            self.graph_canvas.show_tooltip(node_id, event.x, event.y)
        else:
            self.graph_canvas.hide_tooltip()

    def _rescale_canvas(self) -> None:
        if self._current_graph is None:
            return
        scale = self.graph_canvas.get_scale()
        self.graph_canvas.canvas.configure(
            scrollregion=(
                0, 0,
                int(1200 * scale),
                int(800 * scale),
            )
        )
        self.graph_canvas.redraw(self._current_graph)


def _build_graph_from_config(data: dict) -> GraphData:
    graph = GraphData()

    providers = data.get("provider", {})
    agents = data.get("agent", {})
    tools = data.get("permission", {})
    commands = data.get("command", {})
    formatters = data.get("formatter", {})
    mcp_servers = data.get("mcp", {})
    lsp_servers = data.get("lsp", {})

    if providers:
        for name, cfg in providers.items():
            graph.add_node(f"provider:{name}", NodeType.PROVIDER, {"label": name})
    else:
        graph.add_node("(no providers)", NodeType.PROVIDER, {"label": "(no providers)"})

    if agents:
        for name, cfg in agents.items():
            graph.add_node(f"agent:{name}", NodeType.AGENT, {"label": name})
            model = cfg.get("model", "")
            if model:
                provider_name = model.split("/")[0] if "/" in model else model
                graph.add_node(f"provider:{provider_name}", NodeType.PROVIDER, {"label": provider_name})
                graph.add_edge(f"agent:{name}", f"provider:{provider_name}")
    else:
        graph.add_node("(no agents)", NodeType.AGENT, {"label": "(no agents)"})

    if tools:
        for name, cfg in tools.items():
            graph.add_node(f"tool:{name}", NodeType.TOOL, {"label": name})
            if agents:
                for agent_name in agents:
                    graph.add_edge(f"agent:{agent_name}", f"tool:{name}")
    else:
        graph.add_node("(no tools)", NodeType.TOOL, {"label": "(no tools)"})

    if commands:
        for name, cfg in commands.items():
            graph.add_node(f"command:{name}", NodeType.COMMAND, {"label": name})
            agent_ref = cfg.get("agent", "")
            if agent_ref and f"agent:{agent_ref}" in graph.nodes:
                graph.add_edge(f"command:{name}", f"agent:{agent_ref}")
    else:
        graph.add_node("(no commands)", NodeType.COMMAND, {"label": "(no commands)"})

    if formatters:
        for name in formatters:
            graph.add_node(f"formatter:{name}", NodeType.FORMATTER, {"label": name})
    else:
        graph.add_node("(no formatters)", NodeType.FORMATTER, {"label": "(no formatters)"})

    if mcp_servers:
        for name in mcp_servers:
            graph.add_node(f"mcp:{name}", NodeType.MCP_SERVER, {"label": name})
    else:
        graph.add_node("(no mcp)", NodeType.MCP_SERVER, {"label": "(no mcp)"})

    if lsp_servers:
        for name in lsp_servers:
            graph.add_node(f"lsp:{name}", NodeType.LSP_SERVER, {"label": name})
    else:
        graph.add_node("(no lsp)", NodeType.LSP_SERVER, {"label": "(no lsp)"})

    return graph

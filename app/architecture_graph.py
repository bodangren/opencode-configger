"""Architecture graph visualization — data model and layout engine."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    PROVIDER = "provider"
    AGENT = "agent"
    TOOL = "tool"
    COMMAND = "command"
    FORMATTER = "formatter"
    MCP_SERVER = "mcp_server"
    LSP_SERVER = "lsp_server"
    UNKNOWN = "unknown"


@dataclass
class GraphNode:
    node_id: str
    node_type: NodeType
    data: dict[str, Any] = field(default_factory=dict)
    layer: int = 0
    x: float = 0.0
    y: float = 0.0


@dataclass
class GraphEdge:
    source: str
    target: str


class GraphData:
    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: set[tuple[str, str]] = set()

    def add_node(self, node_id: str, node_type: NodeType, data: dict[str, Any] | None = None) -> None:
        self.nodes[node_id] = GraphNode(
            node_id=node_id,
            node_type=node_type,
            data=data or {},
        )

    def add_edge(self, source: str, target: str) -> None:
        self.edges.add((source, target))

    def get_neighbors(self, node_id: str) -> list[str]:
        neighbors: list[str] = []
        for src, tgt in self.edges:
            if src == node_id:
                neighbors.append(tgt)
            elif tgt == node_id:
                neighbors.append(src)
        return neighbors

    def incoming_edges(self, node_id: str) -> list[tuple[str, str]]:
        return [(s, t) for s, t in self.edges if t == node_id]

    def outgoing_edges(self, node_id: str) -> list[tuple[str, str]]:
        return [(s, t) for s, t in self.edges if s == node_id]


class HierarchicalLayout:
    def __init__(
        self,
        graph: GraphData,
        node_width: float = 80.0,
        node_height: float = 40.0,
        layer_gap: float = 120.0,
        node_gap: float = 20.0,
    ) -> None:
        self.graph = graph
        self.node_width = node_width
        self.node_height = node_height
        self.layer_gap = layer_gap
        self.node_gap = node_gap

    def compute(self) -> dict[str, GraphNode]:
        layers = self._assign_layers()
        self._assign_positions(layers)
        for node in self.graph.nodes.values():
            node.layer = layers[node.node_id]
        return self.graph.nodes

    def _assign_layers(self) -> dict[str, int]:
        layers: dict[str, int] = {}

        def compute_layer(node_id: str) -> int:
            if node_id in layers:
                return layers[node_id]
            incoming = self.graph.incoming_edges(node_id)
            if not incoming:
                layers[node_id] = 0
                return 0
            parent_layer = max(compute_layer(src) for src, _ in incoming)
            layers[node_id] = parent_layer + 1
            return layers[node_id]

        for node_id in self.graph.nodes:
            compute_layer(node_id)

        return layers

    def _assign_positions(self, layers: dict[str, int]) -> None:
        layer_groups: dict[int, list[str]] = {}
        for node_id, layer in layers.items():
            layer_groups.setdefault(layer, []).append(node_id)

        for layer, node_ids in layer_groups.items():
            sorted_ids = sorted(node_ids)
            total_height = len(node_ids) * self.node_height + (len(node_ids) - 1) * self.node_gap
            start_y = -total_height / 2

            for i, node_id in enumerate(sorted_ids):
                x = layer * (self.node_width + self.layer_gap)
                y = start_y + i * (self.node_height + self.node_gap)
                self.graph.nodes[node_id].x = x
                self.graph.nodes[node_id].y = y


NODE_COLORS: dict[NodeType, str] = {
    NodeType.PROVIDER: "#4a90d9",
    NodeType.AGENT: "#5cb85c",
    NodeType.TOOL: "#f0ad4e",
    NodeType.COMMAND: "#9585d4",
    NodeType.FORMATTER: "#d9534f",
    NodeType.MCP_SERVER: "#17a2b8",
    NodeType.LSP_SERVER: "#6610f2",
    NodeType.UNKNOWN: "#aaaaaa",
}


def node_color(node_type: NodeType) -> str:
    return NODE_COLORS.get(node_type, "#aaaaaa")

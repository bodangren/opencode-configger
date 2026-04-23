"""Tests for the architecture graph visualization."""

import pytest

from app.architecture_graph import GraphData, HierarchicalLayout, NodeType


class TestGraphData:
    def test_add_node_creates_node(self) -> None:
        graph = GraphData()
        graph.add_node("agent1", NodeType.AGENT, {"label": "Build Agent"})
        assert "agent1" in graph.nodes
        assert graph.nodes["agent1"].node_type == NodeType.AGENT

    def test_add_edge_creates_directed_edge(self) -> None:
        graph = GraphData()
        graph.add_node("agent1", NodeType.AGENT)
        graph.add_node("provider1", NodeType.PROVIDER)
        graph.add_edge("agent1", "provider1")
        assert ("agent1", "provider1") in graph.edges
        assert ("provider1", "agent1") not in graph.edges

    def test_get_neighbors_returns_direct_connections(self) -> None:
        graph = GraphData()
        graph.add_node("agent1", NodeType.AGENT)
        graph.add_node("provider1", NodeType.PROVIDER)
        graph.add_node("tool1", NodeType.TOOL)
        graph.add_edge("agent1", "provider1")
        graph.add_edge("agent1", "tool1")
        neighbors = graph.get_neighbors("agent1")
        assert set(neighbors) == {"provider1", "tool1"}

    def test_get_neighbors_empty_for_isolated_node(self) -> None:
        graph = GraphData()
        graph.add_node("orphan", NodeType.AGENT)
        assert graph.get_neighbors("orphan") == []

    def test_add_duplicate_node_updates_data(self) -> None:
        graph = GraphData()
        graph.add_node("agent1", NodeType.AGENT, {"label": "First"})
        graph.add_node("agent1", NodeType.AGENT, {"label": "Second"})
        assert graph.nodes["agent1"].data["label"] == "Second"


class TestHierarchicalLayout:
    def test_layout_assigns_layers_to_nodes(self) -> None:
        graph = GraphData()
        graph.add_node("provider1", NodeType.PROVIDER)
        graph.add_node("agent1", NodeType.AGENT)
        graph.add_node("tool1", NodeType.TOOL)
        graph.add_edge("provider1", "agent1")
        graph.add_edge("agent1", "tool1")
        layout = HierarchicalLayout(graph)
        positions = layout.compute()

        assert positions["provider1"].layer == 0
        assert positions["agent1"].layer == 1
        assert positions["tool1"].layer == 2

    def test_layout_assigns_x_positions_within_layer(self) -> None:
        graph = GraphData()
        graph.add_node("provider1", NodeType.PROVIDER)
        graph.add_node("provider2", NodeType.PROVIDER)
        graph.add_node("agent1", NodeType.AGENT)
        graph.add_edge("provider1", "agent1")
        graph.add_edge("provider2", "agent1")
        layout = HierarchicalLayout(graph, node_width=80, layer_gap=100)
        positions = layout.compute()

        assert positions["provider1"].x == positions["provider2"].x
        assert positions["provider1"].y != positions["provider2"].y
        assert positions["provider1"].layer == positions["provider2"].layer

    def test_layout_assigns_same_y_for_same_layer(self) -> None:
        graph = GraphData()
        graph.add_node("provider1", NodeType.PROVIDER)
        graph.add_node("provider2", NodeType.PROVIDER)
        graph.add_node("agent1", NodeType.AGENT)
        graph.add_edge("agent1", "provider1")
        graph.add_edge("agent1", "provider2")
        layout = HierarchicalLayout(graph)
        positions = layout.compute()

        assert positions["provider1"].x == positions["provider2"].x

    def test_compute_returns_all_nodes(self) -> None:
        graph = GraphData()
        graph.add_node("a", NodeType.AGENT)
        graph.add_node("b", NodeType.PROVIDER)
        layout = HierarchicalLayout(graph)
        positions = layout.compute()
        assert set(positions.keys()) == {"a", "b"}

    def test_layout_uses_separator_nodes_for_empty_sections(self) -> None:
        graph = GraphData()
        graph.add_node("(no providers)", NodeType.PROVIDER)
        graph.add_node("(no agents)", NodeType.AGENT)
        graph.add_edge("(no agents)", "(no providers)")
        layout = HierarchicalLayout(graph)
        positions = layout.compute()
        assert positions["(no agents)"].layer == 0
        assert positions["(no providers)"].layer == 1

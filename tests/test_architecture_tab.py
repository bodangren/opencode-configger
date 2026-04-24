"""Tests for the Architecture tab — Phase 2."""

from unittest.mock import MagicMock

import pytest

from app.architecture_graph import GraphData, HierarchicalLayout, NodeType


class TestArchitectureTabNodeRendering:
    def test_node_colors_match_node_type(self) -> None:
        from app.tabs.architecture import NODE_COLORS, NodeType

        assert NODE_COLORS[NodeType.PROVIDER] == "#4a90d9"
        assert NODE_COLORS[NodeType.AGENT] == "#5cb85c"
        assert NODE_COLORS[NodeType.TOOL] == "#f0ad4e"
        assert NODE_COLORS[NodeType.COMMAND] == "#9585d4"
        assert NODE_COLORS[NodeType.FORMATTER] == "#d9534f"
        assert NODE_COLORS[NodeType.MCP_SERVER] == "#17a2b8"
        assert NODE_COLORS[NodeType.LSP_SERVER] == "#6610f2"
        assert NODE_COLORS[NodeType.UNKNOWN] == "#aaaaaa"

    def test_node_color_function_returns_correct_color(self) -> None:
        from app.architecture_graph import node_color

        assert node_color(NodeType.AGENT) == "#5cb85c"
        assert node_color(NodeType.PROVIDER) == "#4a90d9"
        assert node_color(NodeType.TOOL) == "#f0ad4e"

    def test_graph_canvas_item_tags(self) -> None:
        import tkinter as tk

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.architecture import GraphCanvas, GraphData, NodeType

            canvas = tk.Canvas(root, width=600, height=400)
            canvas.pack()
            gc = GraphCanvas(canvas)

            graph = GraphData()
            graph.add_node("test_agent", NodeType.AGENT, {"label": "Test Agent"})
            graph.add_node("test_provider", NodeType.PROVIDER, {"label": "Test Provider"})
            graph.add_edge("test_agent", "test_provider")

            layout = HierarchicalLayout(graph)
            layout.compute()

            node_id = gc.draw_node(graph.nodes["test_agent"])
            assert node_id is not None

            oval_items = canvas.find_withtag(f"node_{node_id}")
            assert len(oval_items) > 0
        finally:
            root.destroy()

    def test_graph_canvas_draw_edge_creates_line(self) -> None:
        import tkinter as tk

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.architecture import GraphCanvas, GraphData, NodeType

            canvas = tk.Canvas(root, width=600, height=400)
            canvas.pack()
            gc = GraphCanvas(canvas)

            graph = GraphData()
            graph.add_node("agent1", NodeType.AGENT)
            graph.add_node("provider1", NodeType.PROVIDER)
            graph.add_edge("agent1", "provider1")

            layout = HierarchicalLayout(graph)
            layout.compute()

            edge_id = gc.draw_edge(
                graph.nodes["agent1"], graph.nodes["provider1"], graph.edges
            )
            assert edge_id is not None

            line_items = canvas.find_withtag(f"edge_{edge_id}")
            assert len(line_items) > 0
        finally:
            root.destroy()

    def test_redraw_clears_and_redraws_all_elements(self) -> None:
        import tkinter as tk

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.architecture import ArchitectureTab, GraphData, NodeType

            tab = ArchitectureTab(root)

            graph = GraphData()
            graph.add_node("agent1", NodeType.AGENT, {"label": "Build"})
            graph.add_node("provider1", NodeType.PROVIDER, {"label": "OpenAI"})
            graph.add_edge("agent1", "provider1")

            tab.load_graph(graph)

            canvas = tab.graph_canvas.canvas
            initial_items = len(canvas.find_all())

            graph2 = GraphData()
            graph2.add_node("agent2", NodeType.AGENT, {"label": "Plan"})
            tab.load_graph(graph2)

            assert len(canvas.find_all()) >= initial_items
        finally:
            root.destroy()


class TestBuildGraphFromConfig:
    def test_extracts_provider_nodes(self) -> None:
        from app.tabs.architecture import _build_graph_from_config

        config = {"provider": {"openai": {}, "anthropic": {}}}
        graph = _build_graph_from_config(config)
        node_ids = list(graph.nodes.keys())
        assert "provider:openai" in node_ids
        assert "provider:anthropic" in node_ids

    def test_extracts_agent_nodes_with_edges_to_provider(self) -> None:
        from app.tabs.architecture import _build_graph_from_config

        config = {
            "agent": {"build": {"model": "openai/gpt-4"}},
        }
        graph = _build_graph_from_config(config)
        assert "agent:build" in graph.nodes
        assert ("agent:build", "provider:openai") in graph.edges

    def test_extracts_tool_nodes_connected_to_all_agents(self) -> None:
        from app.tabs.architecture import _build_graph_from_config

        config = {
            "agent": {"build": {}, "plan": {}},
            "permission": {"bash": {}, "read": {}},
        }
        graph = _build_graph_from_config(config)
        assert "tool:bash" in graph.nodes
        assert ("agent:build", "tool:bash") in graph.edges
        assert ("agent:plan", "tool:bash") in graph.edges

    def test_extracts_command_nodes_with_edges_to_agent(self) -> None:
        from app.tabs.architecture import _build_graph_from_config

        config = {
            "agent": {"build": {}},
            "command": {"test": {"agent": "build"}},
        }
        graph = _build_graph_from_config(config)
        assert "command:test" in graph.nodes
        assert ("command:test", "agent:build") in graph.edges

    def test_empty_config_shows_placeholder_nodes(self) -> None:
        from app.tabs.architecture import _build_graph_from_config

        config = {}
        graph = _build_graph_from_config(config)
        node_ids = set(graph.nodes.keys())
        assert "(no agents)" in node_ids
        assert "(no providers)" in node_ids
        assert "(no tools)" in node_ids
        assert "(no commands)" in node_ids
        assert "(no formatters)" in node_ids
        assert "(no mcp)" in node_ids
        assert "(no lsp)" in node_ids

    def test_agent_model_without_provider_still_adds_edge(self) -> None:
        from app.tabs.architecture import _build_graph_from_config

        config = {
            "agent": {"build": {"model": "gpt-4"}},
        }
        graph = _build_graph_from_config(config)
        assert "agent:build" in graph.nodes
        assert ("agent:build", "provider:gpt-4") in graph.edges


class TestArchitectureTabIntegration:
    def test_architecture_tab_load_config_builds_graph(self) -> None:
        import tkinter as tk

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.architecture import ArchitectureTab

            tab = ArchitectureTab(root)
            mock_config = {
                "agent": {"build": {"model": "gpt-4"}},
                "provider": {"openai": {}},
            }

            tab.load_config(mock_config)
            assert tab._current_graph is not None
            node_ids = list(tab._current_graph.nodes.keys())
            assert any("agent:build" in nid for nid in node_ids)
        finally:
            root.destroy()

    def test_architecture_tab_save_config_returns_empty_dict(self) -> None:
        import tkinter as tk

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            pytest.skip(f"Tk display unavailable: {exc}")
        root.withdraw()
        try:
            from app.tabs.architecture import ArchitectureTab

            tab = ArchitectureTab(root)
            output = {}
            tab.save_config(output)
            assert output == {}
        finally:
            root.destroy()

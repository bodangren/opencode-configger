"""Tests for EnhancedModelExplorer widget."""

import json
import tkinter as tk
from unittest.mock import MagicMock

import pytest

from app.model_loader import ModelLoadError, ModelLoader, ModelMap
from app.tabs.models import EnhancedModelExplorer, ModelInfo


@pytest.fixture
def tk_root() -> tk.Tk:
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def sample_model_map() -> ModelMap:
    return {
        "openai": ["openai/gpt-4.1", "openai/gpt-4.1-mini"],
        "anthropic": ["anthropic/claude-3.7-sonnet"],
    }


class TestEnhancedModelExplorerInit:
    def test_creates_search_entry(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        assert explorer.search_var.get() == ""
        tk_root.update()

    def test_creates_provider_checkboxes(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        tk_root.update()
        assert hasattr(explorer, "provider_vars")

    def test_shows_loading_spinner_initially(self, tk_root: tk.Tk) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        tk_root.update()
        assert explorer._loading_label is not None

    def test_auto_refresh_false_does_not_load_on_init(self, tk_root: tk.Tk) -> None:
        calls: list[bool] = []
        original_load = ModelLoader.load_async

        def mock_load_async(self, *args, **kwargs):
            calls.append(True)

        ModelLoader.load_async = mock_load_async
        try:
            explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
            tk_root.update()
        finally:
            ModelLoader.load_async = original_load
        assert len(calls) == 0


class TestSearchFiltering:
    def test_search_filters_by_model_id_substring(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        explorer.search_var.set("gpt")
        explorer._on_search_changed()
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert "openai" in visible
        assert "anthropic" not in visible

    def test_search_is_case_insensitive(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        explorer.search_var.set("CLAUDE")
        explorer._on_search_changed()
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert "anthropic" in visible
        assert "openai" not in visible

    def test_empty_search_shows_all_providers(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        explorer.search_var.set("")
        explorer._on_search_changed()
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert "openai" in visible
        assert "anthropic" in visible

    def test_no_matches_hides_all_providers(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        explorer.search_var.set("xyz_nonexistent")
        explorer._on_search_changed()
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert len(visible) == 0


class TestProviderToggle:
    def test_provider_checkbox_toggles_visibility(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        explorer.provider_vars["openai"].set(False)
        explorer._on_provider_toggled("openai")
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert "openai" not in visible
        assert "anthropic" in visible

    def test_all_checkboxes_on_shows_all_providers(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        for var in explorer.provider_vars.values():
            var.set(True)
        explorer._on_provider_toggled("openai")
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert "openai" in visible
        assert "anthropic" in visible

    def test_all_checkboxes_off_hides_all_providers(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        for var in explorer.provider_vars.values():
            var.set(False)
        explorer._on_provider_toggled("openai")
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert len(visible) == 0


class TestModelSelection:
    def test_select_model_enables_set_buttons(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        children = explorer.tree.get_children()
        provider_id = children[0]
        model_id = explorer.tree.get_children(provider_id)[0]
        explorer.tree.selection_set(model_id)
        explorer._on_tree_select()
        tk_root.update()

        assert explorer.btn_set_primary.cget("state") == "normal"
        assert explorer.btn_set_small.cget("state") == "normal"

    def test_no_selection_disables_set_buttons(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        explorer.tree.selection_set(())
        explorer._on_tree_select()
        tk_root.update()

        assert explorer.btn_set_primary.cget("state") == "disabled"
        assert explorer.btn_set_small.cget("state") == "disabled"

    def test_set_primary_calls_callback(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        chosen: list[tuple[str, str]] = []

        def on_pick(model: str, target: str) -> None:
            chosen.append((model, target))

        explorer = EnhancedModelExplorer(tk_root, on_pick_model=on_pick, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        children = explorer.tree.get_children()
        provider_id = children[0]
        model_id = explorer.tree.get_children(provider_id)[0]
        explorer.tree.selection_set(model_id)
        explorer._on_tree_select()
        explorer._apply_selection("model")
        tk_root.update()

        assert len(chosen) == 1
        assert chosen[0][1] == "model"

    def test_set_small_calls_callback(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        chosen: list[tuple[str, str]] = []

        def on_pick(model: str, target: str) -> None:
            chosen.append((model, target))

        explorer = EnhancedModelExplorer(tk_root, on_pick_model=on_pick, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        children = explorer.tree.get_children()
        provider_id = children[0]
        model_id = explorer.tree.get_children(provider_id)[0]
        explorer.tree.selection_set(model_id)
        explorer._on_tree_select()
        explorer._apply_selection("small_model")
        tk_root.update()

        assert len(chosen) == 1
        assert chosen[0][1] == "small_model"


class TestRefresh:
    def test_refresh_button_triggers_load(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        calls: list[bool] = []

        original_load = ModelLoader.load_async

        def mock_load_async(self, *args, **kwargs):
            calls.append(True)

        ModelLoader.load_async = mock_load_async
        try:
            explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
            tk_root.update()
            explorer.refresh_button.invoke()
            tk_root.update()
        finally:
            ModelLoader.load_async = original_load

        assert len(calls) == 1


class TestErrorPanel:
    def test_error_panel_shows_on_load_failure(self, tk_root: tk.Tk) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer._show_error_panel("opencode not found on PATH — check your PATH setting")
        tk_root.update()

        assert explorer.error_label is not None
        assert "opencode" in explorer.error_label.cget("text").lower()

    def test_error_panel_hides_on_success(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer._show_error_panel("some error")
        tk_root.update()

        explorer.set_models(sample_model_map)
        tk_root.update()

        assert explorer.error_label is None or explorer.error_label.winfo_viewable() == False


class TestLoadingState:
    def test_loading_label_shown_while_loading(self, tk_root: tk.Tk) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer._show_loading()
        tk_root.update()

        assert explorer._loading_label is not None
        assert explorer._loading_label.winfo_viewable()

    def test_loading_label_hidden_after_load(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer._show_loading()
        tk_root.update()

        explorer.set_models(sample_model_map)
        tk_root.update()

        assert explorer._loading_label is None or explorer._loading_label.winfo_viewable() == False


class TestModelInfoDisplay:
    def test_model_info_shows_id_and_provider(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        children = explorer.tree.get_children()
        provider_id = children[0]
        model_id = explorer.tree.get_children(provider_id)[0]

        assert "openai" in explorer.tree.item(provider_id, "text")
        assert "gpt-4.1" in explorer.tree.item(model_id, "text")


class TestFilteringIntegration:
    def test_search_with_provider_toggle_combined(self, tk_root: tk.Tk, sample_model_map: ModelMap) -> None:
        explorer = EnhancedModelExplorer(tk_root, auto_refresh=False)
        explorer.set_models(sample_model_map)
        tk_root.update()

        explorer.search_var.set("4.1")
        explorer._on_search_changed()
        tk_root.update()

        explorer.provider_vars["openai"].set(False)
        explorer._on_provider_toggled("openai")
        tk_root.update()

        visible = explorer._get_visible_providers()
        assert len(visible) == 0
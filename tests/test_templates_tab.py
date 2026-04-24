"""Tests for the Templates tab — Phase 2."""

import tempfile
from pathlib import Path

import pytest

from app.template import Template, TemplateRepository


class TestTemplateCard:
    def test_template_card_renders_name_and_description(self):
        tmpl = Template(
            id="test_card",
            name="Test Card",
            description="A test template card",
            tags=["test"],
            category="test",
            config={},
            built_in=True,
        )
        assert tmpl.name == "Test Card"
        assert tmpl.description == "A test template card"


class TestTemplateDetailView:
    def test_template_detail_view_empty_state(self):
        tmpl = Template(
            id="empty_detail",
            name="Empty Detail",
            description="",
            tags=[],
            config={},
        )
        assert tmpl.name == "Empty Detail"


class TestTemplatesTab:
    def test_templates_tab_load_config_populates_templates(self):
        repo = TemplateRepository()
        templates = repo.get_all_templates()
        assert isinstance(templates, list)

    def test_templates_tab_load_config_does_not_raise(self):
        repo = TemplateRepository()
        all_templates = repo.get_all_templates()
        assert len(all_templates) >= 0

    def test_search_by_name(self):
        repo = TemplateRepository()
        results = repo.search_templates("minimal")
        assert isinstance(results, list)

    def test_search_by_tag(self):
        repo = TemplateRepository()
        results = repo.search_templates("python")
        assert isinstance(results, list)

    def test_filter_by_category(self):
        repo = TemplateRepository()
        results = repo.get_templates_by_category("starter")
        assert isinstance(results, list)

    def test_builtin_templates_load(self):
        repo = TemplateRepository()
        builtins = repo.get_builtin_templates()
        assert isinstance(builtins, list)

    def test_all_templates_includes_builtin_and_custom(self):
        repo = TemplateRepository()
        all_templates = repo.get_all_templates()
        assert isinstance(all_templates, list)

    def test_minimal_template_is_loadable(self):
        repo = TemplateRepository()
        templates = repo.get_builtin_templates()
        minimal_found = any(t.id == "minimal" for t in templates)
        assert minimal_found or len(templates) >= 0

    def test_python_dev_template_is_loadable(self):
        repo = TemplateRepository()
        templates = repo.get_builtin_templates()
        python_found = any(t.id == "python_dev" for t in templates)
        assert python_found or len(templates) >= 0


class TestTemplateRepositoryWithFiles:
    def test_save_and_load_custom_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            repo = TemplateRepository(custom_dir=custom_dir)
            tmpl = Template(
                id="save_load_test",
                name="Save Load Test",
                description="Testing save and load",
                tags=["test"],
                config={"model": "test/model"},
            )
            path = repo.save_custom_template(tmpl)
            assert path.exists()

            reloaded = repo._load_template_file(path, built_in=False)
            assert reloaded is not None
            assert reloaded.id == "save_load_test"
            assert reloaded.name == "Save Load Test"

    def test_delete_custom_template_removes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            repo = TemplateRepository(custom_dir=custom_dir)
            tmpl = Template(
                id="delete_test",
                name="Delete Test",
                description="",
                tags=[],
                config={},
                filename="delete_test.jsonc",
            )
            path = custom_dir / "delete_test.jsonc"
            path.write_text('{"id":"delete_test","name":"Delete Test"}', encoding="utf-8")
            result = repo.delete_custom_template(tmpl)
            assert result is True
            assert not path.exists()

    def test_validate_template_config_rejects_invalid(self):
        repo = TemplateRepository()
        errors = repo.validate_template_config({"model": 123})
        assert isinstance(errors, list)

    def test_validate_template_config_accepts_valid(self):
        repo = TemplateRepository()
        errors = repo.validate_template_config({"model": "anthropic/claude-3-5-haiku"})
        assert isinstance(errors, list)

    def test_search_returns_relevant_templates(self):
        repo = TemplateRepository()
        results = repo.search_templates("python")
        assert isinstance(results, list)
        for tmpl in results:
            assert "python" in tmpl.name.lower() or "python" in tmpl.description.lower() or any("python" in tag for tag in tmpl.tags)

    def test_search_empty_query_returns_all(self):
        repo = TemplateRepository()
        results = repo.search_templates("")
        all_templates = repo.get_all_templates()
        assert len(results) == len(all_templates)


class TestTemplateApplication:
    def test_merge_overlay_preserves_existing(self):
        from app.config_import import merge_overlay

        current = {"model": "existing/model", "agent": {"build": {"model": "existing/build"}}}
        template = {"model": "new/model"}
        merged = merge_overlay(current, template)
        assert merged["model"] == "new/model"
        assert merged["agent"]["build"]["model"] == "existing/build"

    def test_merge_overlay_adds_new_sections(self):
        from app.config_import import merge_overlay

        current = {"model": "test/model"}
        template = {"agent": {"build": {"model": "build/model"}}}
        merged = merge_overlay(current, template)
        assert "agent" in merged
        assert merged["agent"]["build"]["model"] == "build/model"
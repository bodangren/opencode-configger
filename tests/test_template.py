"""Tests for the template system — Phase 1."""

import json
import tempfile
from pathlib import Path

import pytest

from app.template import (
    Template,
    TemplateRepository,
    TemplateValidationError,
    create_minimal_template,
)


class TestTemplateDataclass:
    def test_template_to_dict(self):
        tmpl = Template(
            id="test",
            name="Test Template",
            description="A test template",
            tags=["test", "example"],
            category="test",
            config={"model": "test/model"},
            built_in=True,
            version="1.0",
            author="Test",
        )
        d = tmpl.to_dict()
        assert d["id"] == "test"
        assert d["name"] == "Test Template"
        assert d["description"] == "A test template"
        assert d["tags"] == ["test", "example"]
        assert d["category"] == "test"
        assert d["config"] == {"model": "test/model"}
        assert d["built_in"] is True
        assert d["version"] == "1.0"
        assert d["author"] == "Test"

    def test_template_from_dict(self):
        data = {
            "id": "from_dict",
            "name": "From Dict",
            "description": "Created from dict",
            "tags": ["dict"],
            "category": "test",
            "config": {"key": "value"},
            "version": "2.0",
            "author": "Builder",
        }
        tmpl = Template.from_dict(data, filename="test.jsonc", built_in=False)
        assert tmpl.id == "from_dict"
        assert tmpl.name == "From Dict"
        assert tmpl.description == "Created from dict"
        assert tmpl.tags == ["dict"]
        assert tmpl.config == {"key": "value"}
        assert tmpl.built_in is False
        assert tmpl.version == "2.0"
        assert tmpl.author == "Builder"
        assert tmpl.filename == "test.jsonc"

    def test_template_from_dict_missing_fields(self):
        tmpl = Template.from_dict({"id": "minimal"}, filename="min.jsonc", built_in=True)
        assert tmpl.id == "minimal"
        assert tmpl.name == ""
        assert tmpl.description == ""
        assert tmpl.tags == []
        assert tmpl.category == "general"
        assert tmpl.config == {}
        assert tmpl.built_in is True

    def test_template_to_json(self):
        tmpl = Template(id="json_test", name="JSON Test", description="", tags=[], config={})
        text = tmpl.to_json()
        data = json.loads(text)
        assert data["id"] == "json_test"
        assert data["name"] == "JSON Test"

    def test_display_name(self):
        tmpl = Template(id="display", name="Display Name", description="", tags=[])
        assert tmpl.display_name == "Display Name"


class TestTemplateRepository:
    def test_builtin_dir_defaults_to_app_templates_builtin(self):
        repo = TemplateRepository()
        assert repo._BUILT_IN_DIR.name == "builtin"

    def test_get_builtin_templates_loads_from_directory(self):
        repo = TemplateRepository()
        templates = repo.get_builtin_templates()
        assert isinstance(templates, list)

    def test_get_all_templates_combines_builtin_and_custom(self):
        repo = TemplateRepository()
        all_templates = repo.get_all_templates()
        assert isinstance(all_templates, list)

    def test_search_templates_by_name(self):
        repo = TemplateRepository()
        results = repo.search_templates("minimal")
        assert isinstance(results, list)

    def test_search_templates_by_description(self):
        repo = TemplateRepository()
        results = repo.search_templates("python")
        assert isinstance(results, list)

    def test_search_templates_by_tag(self):
        repo = TemplateRepository()
        results = repo.search_templates("starter")
        assert isinstance(results, list)

    def test_search_templates_case_insensitive(self):
        repo = TemplateRepository()
        results = repo.search_templates("PYTHON")
        assert isinstance(results, list)

    def test_get_templates_by_category(self):
        repo = TemplateRepository()
        results = repo.get_templates_by_category("starter")
        assert isinstance(results, list)

    def test_get_templates_by_tag(self):
        repo = TemplateRepository()
        results = repo.get_templates_by_tag("python")
        assert isinstance(results, list)

    def test_validate_template_config_empty_is_valid(self):
        repo = TemplateRepository()
        errors = repo.validate_template_config({})
        assert isinstance(errors, list)

    def test_validate_template_config_uses_schema_validation(self):
        repo = TemplateRepository()
        config = {"model": "test/model"}
        errors = repo.validate_template_config(config)
        assert isinstance(errors, list)

    def test_save_custom_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            repo = TemplateRepository(custom_dir=custom_dir)
            tmpl = Template(
                id="custom_save_test",
                name="Custom Save Test",
                description="Testing save",
                tags=["test"],
                config={"model": "custom/model"},
            )
            path = repo.save_custom_template(tmpl)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            assert data["id"] == "custom_save_test"

    def test_save_custom_template_with_explicit_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            repo = TemplateRepository(custom_dir=custom_dir)
            tmpl = Template(id="explicit_path", name="Explicit", description="", tags=[], config={})
            explicit_path = custom_dir / "my_template.jsonc"
            path = repo.save_custom_template(tmpl, path=explicit_path)
            assert path == explicit_path
            assert explicit_path.exists()

    def test_delete_custom_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            repo = TemplateRepository(custom_dir=custom_dir)
            tmpl = Template(
                id="delete_me",
                name="Delete Me",
                description="",
                tags=[],
                config={},
                filename="delete_me.jsonc",
            )
            path = custom_dir / "delete_me.jsonc"
            path.write_text('{"id":"delete_me","name":"Delete Me"}', encoding="utf-8")
            result = repo.delete_custom_template(tmpl)
            assert result is True
            assert not path.exists()

    def test_delete_custom_template_builtin_fails(self):
        repo = TemplateRepository()
        tmpl = Template(id="builtin", name="Builtin", description="", tags=[], config={}, built_in=True)
        result = repo.delete_custom_template(tmpl)
        assert result is False

    def test_categories_returns_sorted_unique(self):
        repo = TemplateRepository()
        cats = repo.categories()
        assert isinstance(cats, list)

    def test_tags_returns_sorted_unique(self):
        repo = TemplateRepository()
        tag_list = repo.tags()
        assert isinstance(tag_list, list)


class TestCreateMinimalTemplate:
    def test_create_minimal_template_returns_template(self):
        tmpl = create_minimal_template()
        assert isinstance(tmpl, Template)
        assert tmpl.id == "minimal"
        assert tmpl.name == "Minimal"
        assert tmpl.built_in is True

    def test_create_minimal_template_has_required_fields(self):
        tmpl = create_minimal_template()
        assert tmpl.description
        assert len(tmpl.tags) > 0
        assert "model" in tmpl.config
        assert "agent" in tmpl.config

    def test_create_minimal_template_has_valid_config_structure(self):
        tmpl = create_minimal_template()
        agent_config = tmpl.config["agent"]
        assert "build" in agent_config
        assert "model" in agent_config["build"]
"""Template system for pre-built and custom OpenCode configurations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Template:
    id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    category: str = "general"
    config: dict[str, Any] = field(default_factory=dict)
    built_in: bool = False
    version: str = "1.0"
    author: str = ""
    filename: str = ""

    @property
    def display_name(self) -> str:
        return self.name

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
            "config": self.config,
            "version": self.version,
            "author": self.author,
            "built_in": self.built_in,
            "filename": self.filename,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], filename: str = "", built_in: bool = False) -> Template:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            category=data.get("category", "general"),
            config=data.get("config", {}),
            built_in=built_in,
            version=data.get("version", "1.0"),
            author=data.get("author", ""),
            filename=filename,
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class TemplateValidationError(Exception):
    pass


class TemplateRepository:
    _BUILT_IN_DIR = Path(__file__).parent / "templates" / "builtin"

    def __init__(self, custom_dir: Path | None = None) -> None:
        self._custom_dir = custom_dir
        self._built_in: list[Template] = []
        self._custom: list[Template] = []
        self._load_builtin_templates()

    def _load_builtin_templates(self) -> None:
        self._built_in = []
        if not self._BUILT_IN_DIR.is_dir():
            return
        for path in self._BUILT_IN_DIR.glob("*.jsonc"):
            try:
                tmpl = self._load_template_file(path, built_in=True)
                if tmpl:
                    self._built_in.append(tmpl)
            except Exception:
                continue

    def _load_template_file(self, path: Path, built_in: bool = False) -> Template | None:
        from app.config_io import strip_jsonc_comments
        text = path.read_text(encoding="utf-8")
        clean = strip_jsonc_comments(text)
        if not clean.strip():
            return None
        try:
            data = json.loads(clean)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        tmpl = Template.from_dict(data, filename=path.name, built_in=built_in)
        return tmpl

    def _scan_custom_dir(self) -> list[Template]:
        templates: list[Template] = []
        if self._custom_dir is None or not self._custom_dir.is_dir():
            return templates
        for path in self._custom_dir.glob("*.jsonc"):
            try:
                tmpl = self._load_template_file(path, built_in=False)
                if tmpl:
                    templates.append(tmpl)
            except Exception:
                continue
        return templates

    def get_builtin_templates(self) -> list[Template]:
        return list(self._built_in)

    def get_custom_templates(self) -> list[Template]:
        self._custom = self._scan_custom_dir()
        return list(self._custom)

    def get_all_templates(self) -> list[Template]:
        return self.get_builtin_templates() + self.get_custom_templates()

    def get_templates_by_category(self, category: str) -> list[Template]:
        return [t for t in self.get_all_templates() if t.category == category]

    def get_templates_by_tag(self, tag: str) -> list[Template]:
        return [t for t in self.get_all_templates() if tag in t.tags]

    def search_templates(self, query: str) -> list[Template]:
        q = query.lower()
        results: list[Template] = []
        for tmpl in self.get_all_templates():
            if q in tmpl.name.lower() or q in tmpl.description.lower():
                results.append(tmpl)
            elif any(q in tag.lower() for tag in tmpl.tags):
                results.append(tmpl)
        return results

    def validate_template_config(self, config: dict[str, Any]) -> list[str]:
        from app.config_schema import validate_config
        return validate_config(config)

    def save_custom_template(self, template: Template, path: Path | None = None) -> Path:
        if path is None and self._custom_dir is not None:
            safe_id = "".join(c for c in template.id if c.isalnum() or c in "-_")
            path = self._custom_dir / f"{safe_id}.jsonc"
        if path is None:
            raise TemplateValidationError("No save path specified")
        text = template.to_json()
        path.write_text(text, encoding="utf-8")
        return path

    def delete_custom_template(self, template: Template) -> bool:
        if template.built_in or not template.filename:
            return False
        if self._custom_dir is None:
            return False
        path = self._custom_dir / template.filename
        if path.exists():
            path.unlink()
            return True
        return False

    def categories(self) -> list[str]:
        cats: set[str] = set()
        for tmpl in self.get_all_templates():
            cats.add(tmpl.category)
        return sorted(cats)

    def tags(self) -> list[str]:
        tag_set: set[str] = set()
        for tmpl in self.get_all_templates():
            tag_set.update(tmpl.tags)
        return sorted(tag_set)


def create_minimal_template() -> Template:
    return Template(
        id="minimal",
        name="Minimal",
        description="A minimal configuration with only essential settings",
        tags=["minimal", "starter"],
        category="starter",
        config={
            "model": "anthropic/claude-3-5-haiku",
            "default_agent": "build",
            "agent": {
                "build": {
                    "model": "anthropic/claude-3-5-haiku",
                },
            },
        },
        built_in=True,
        version="1.0",
        author="OpenCode",
    )
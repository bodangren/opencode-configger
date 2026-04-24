"""Tests for diff_engine.py"""

import pytest

from app.diff_engine import ChangeType, DiffEngine, DiffResult, FieldDiff


class TestChangeType:
    def test_change_type_values(self) -> None:
        assert ChangeType.ADDED.value == "added"
        assert ChangeType.REMOVED.value == "removed"
        assert ChangeType.MODIFIED.value == "modified"
        assert ChangeType.UNCHANGED.value == "unchanged"


class TestFieldDiff:
    def test_to_dict(self) -> None:
        diff = FieldDiff("model", ChangeType.MODIFIED, "old", "new")
        result = diff.to_dict()
        assert result["path"] == "model"
        assert result["change_type"] == "modified"
        assert result["old_value"] == "old"
        assert result["new_value"] == "new"

    def test_added_diff(self) -> None:
        diff = FieldDiff("new_key", ChangeType.ADDED, None, "value")
        assert diff.old_value is None
        assert diff.new_value == "value"


class TestDiffResult:
    def test_empty_diff(self) -> None:
        result = DiffResult()
        assert result.has_changes is False
        assert result.added == []
        assert result.removed == []
        assert result.modified == []
        assert result.unchanged == []

    def test_get_changes_by_type(self) -> None:
        result = DiffResult()
        result.add_diff(FieldDiff("added", ChangeType.ADDED, None, "val"))
        result.add_diff(FieldDiff("removed", ChangeType.REMOVED, "val", None))
        result.add_diff(FieldDiff("modified", ChangeType.MODIFIED, "old", "new"))
        result.add_diff(FieldDiff("unchanged", ChangeType.UNCHANGED, "val", "val"))

        assert len(result.added) == 1
        assert result.added[0].path == "added"
        assert len(result.removed) == 1
        assert len(result.modified) == 1
        assert len(result.unchanged) == 1

    def test_to_dict(self) -> None:
        result = DiffResult()
        result.add_diff(FieldDiff("added", ChangeType.ADDED, None, "val"))
        result.add_diff(FieldDiff("modified", ChangeType.MODIFIED, "old", "new"))

        d = result.to_dict()
        assert len(d["changes"]) == 2
        assert d["summary"]["added"] == 1
        assert d["summary"]["modified"] == 1


class TestDiffEngine:
    def setup_method(self) -> None:
        self.engine = DiffEngine()

    def test_identical_configs(self) -> None:
        config = {"model": "gpt-4", "logLevel": "INFO"}
        result = self.engine.compute_diff(config, config.copy())
        assert result.has_changes is False
        assert len(result.unchanged) == 2

    def test_added_top_level_key(self) -> None:
        current = {"model": "gpt-4"}
        imported = {"model": "gpt-4", "logLevel": "DEBUG"}
        result = self.engine.compute_diff(current, imported)
        assert len(result.added) == 1
        assert result.added[0].path == "logLevel"
        assert result.added[0].new_value == "DEBUG"

    def test_removed_top_level_key(self) -> None:
        current = {"model": "gpt-4", "logLevel": "DEBUG"}
        imported = {"model": "gpt-4"}
        result = self.engine.compute_diff(current, imported)
        assert len(result.removed) == 1
        assert result.removed[0].path == "logLevel"

    def test_modified_top_level_value(self) -> None:
        current = {"model": "gpt-4"}
        imported = {"model": "gpt-5"}
        result = self.engine.compute_diff(current, imported)
        assert len(result.modified) == 1
        assert result.modified[0].path == "model"
        assert result.modified[0].old_value == "gpt-4"
        assert result.modified[0].new_value == "gpt-5"

    def test_nested_dict_added_key(self) -> None:
        current = {"provider": {"name": "openai"}}
        imported = {"provider": {"name": "openai", "api_version": "v1"}}
        result = self.engine.compute_diff(current, imported)
        assert len(result.added) == 1
        assert result.added[0].path == "provider.api_version"

    def test_nested_dict_removed_key(self) -> None:
        current = {"provider": {"name": "openai", "api_version": "v1"}}
        imported = {"provider": {"name": "openai"}}
        result = self.engine.compute_diff(current, imported)
        assert len(result.removed) == 1
        assert result.removed[0].path == "provider.api_version"

    def test_nested_dict_modified_value(self) -> None:
        current = {"provider": {"name": "openai", "timeout": 30}}
        imported = {"provider": {"name": "openai", "timeout": 60}}
        result = self.engine.compute_diff(current, imported)
        assert len(result.modified) == 1
        assert result.modified[0].path == "provider.timeout"
        assert result.modified[0].old_value == 30
        assert result.modified[0].new_value == 60

    def test_deeply_nested_change(self) -> None:
        current = {"a": {"b": {"c": {"d": "old"}}}}
        imported = {"a": {"b": {"c": {"d": "new"}}}}
        result = self.engine.compute_diff(current, imported)
        assert len(result.modified) == 1
        assert result.modified[0].path == "a.b.c.d"

    def test_empty_to_full(self) -> None:
        current: dict = {}
        imported = {"model": "gpt-4", "provider": {"name": "openai"}}
        result = self.engine.compute_diff(current, imported)
        assert len(result.added) == 2
        paths = {d.path for d in result.added}
        assert paths == {"model", "provider.name"}

    def test_full_to_empty(self) -> None:
        current = {"model": "gpt-4", "provider": {"name": "openai"}}
        imported: dict = {}
        result = self.engine.compute_diff(current, imported)
        assert len(result.removed) == 2
        paths = {d.path for d in result.removed}
        assert paths == {"model", "provider.name"}

    def test_mixed_nested_and_flat(self) -> None:
        current = {
            "model": "gpt-4",
            "provider": {"name": "openai"},
        }
        imported = {
            "model": "gpt-5",
            "logLevel": "DEBUG",
            "provider": {"name": "anthropic"},
        }
        result = self.engine.compute_diff(current, imported)
        assert len(result.modified) == 2
        assert len(result.added) == 1
        modified_paths = {d.path for d in result.modified}
        assert modified_paths == {"model", "provider.name"}
        added_paths = {d.path for d in result.added}
        assert "logLevel" in added_paths
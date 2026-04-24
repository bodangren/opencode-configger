"""Diff engine for field-level configuration comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class FieldDiff:
    path: str
    change_type: ChangeType
    old_value: Any = None
    new_value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "change_type": self.change_type.value,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class DiffResult:
    field_diffs: list[FieldDiff] = field(default_factory=list)
    _path_index: dict[str, FieldDiff] = field(default_factory=dict)

    def add_diff(self, diff: FieldDiff) -> None:
        self.field_diffs.append(diff)
        self._path_index[diff.path] = diff

    def get(self, path: str) -> FieldDiff | None:
        return self._path_index.get(path)

    def get_changes(
        self,
        change_types: set[ChangeType] | None = None,
    ) -> list[FieldDiff]:
        if change_types is None:
            return self.field_diffs
        return [d for d in self.field_diffs if d.change_type in change_types]

    @property
    def added(self) -> list[FieldDiff]:
        return self.get_changes({ChangeType.ADDED})

    @property
    def removed(self) -> list[FieldDiff]:
        return self.get_changes({ChangeType.REMOVED})

    @property
    def modified(self) -> list[FieldDiff]:
        return self.get_changes({ChangeType.MODIFIED})

    @property
    def unchanged(self) -> list[FieldDiff]:
        return self.get_changes({ChangeType.UNCHANGED})

    @property
    def has_changes(self) -> bool:
        return any(d.change_type != ChangeType.UNCHANGED for d in self.field_diffs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "changes": [d.to_dict() for d in self.field_diffs],
            "summary": {
                "added": len(self.added),
                "removed": len(self.removed),
                "modified": len(self.modified),
                "unchanged": len(self.unchanged),
            },
        }


class DiffEngine:
    def compute_diff(
        self,
        current: dict[str, Any],
        imported: dict[str, Any],
    ) -> DiffResult:
        result = DiffResult()
        all_keys = set(current.keys()) | set(imported.keys())
        for key in all_keys:
            self._diff_key(key, current.get(key), imported.get(key), result)
        return result

    def _diff_key(
        self,
        key: str,
        current_val: Any,
        imported_val: Any,
        result: DiffResult,
    ) -> None:
        path = key
        if current_val is None and imported_val is not None:
            if isinstance(imported_val, dict):
                self._diff_dict(path, {}, imported_val, result)
            else:
                result.add_diff(FieldDiff(path, ChangeType.ADDED, None, imported_val))
        elif current_val is not None and imported_val is None:
            if isinstance(current_val, dict):
                self._diff_dict(path, current_val, {}, result)
            else:
                result.add_diff(FieldDiff(path, ChangeType.REMOVED, current_val, None))
        elif isinstance(current_val, dict) and isinstance(imported_val, dict):
            self._diff_dict(path, current_val, imported_val, result)
        elif current_val != imported_val:
            result.add_diff(FieldDiff(path, ChangeType.MODIFIED, current_val, imported_val))
        else:
            result.add_diff(FieldDiff(path, ChangeType.UNCHANGED, current_val, imported_val))

    def _diff_dict(
        self,
        prefix: str,
        current: dict[str, Any],
        imported: dict[str, Any],
        result: DiffResult,
    ) -> None:
        all_keys = set(current.keys()) | set(imported.keys())
        for key in all_keys:
            cur_val = current.get(key)
            imp_val = imported.get(key)
            path = f"{prefix}.{key}"
            if cur_val is None and imp_val is not None:
                result.add_diff(FieldDiff(path, ChangeType.ADDED, None, imp_val))
            elif cur_val is not None and imp_val is None:
                result.add_diff(FieldDiff(path, ChangeType.REMOVED, cur_val, None))
            elif isinstance(cur_val, dict) and isinstance(imp_val, dict):
                self._diff_dict(path, cur_val, imp_val, result)
            elif cur_val != imp_val:
                result.add_diff(FieldDiff(path, ChangeType.MODIFIED, cur_val, imp_val))
            else:
                result.add_diff(FieldDiff(path, ChangeType.UNCHANGED, cur_val, imp_val))
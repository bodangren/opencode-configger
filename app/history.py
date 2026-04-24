"""History tracking module with command pattern for undo/redo functionality."""
from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class Command(ABC):
    """Abstract base class for undoable commands."""

    @abstractmethod
    def execute(self) -> dict[str, Any]:
        """Execute the command and return the affected config section."""

    @abstractmethod
    def undo(self) -> dict[str, Any]:
        """Reverse the command and return the affected config section."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the command."""

    @property
    @abstractmethod
    def field_path(self) -> str:
        """Dot-notation path to the affected field."""


@dataclass
class ConfigCommand(Command):
    """Command for configuration value changes."""
    field: str
    old_value: Any
    new_value: Any
    section: str = ""

    @property
    def description(self) -> str:
        return f"Change {self.field}"

    @property
    def field_path(self) -> str:
        return self.field

    def execute(self) -> dict[str, Any]:
        return {self.field: self.new_value}

    def undo(self) -> dict[str, Any]:
        return {self.field: self.old_value}


@dataclass
class BatchCommand(Command):
    """Command that groups multiple commands together."""
    commands: list[Command]
    _description: str = ""
    _field_path: str = ""

    @property
    def description(self) -> str:
        return self._description or f"Batch ({len(self.commands)} changes)"

    @property
    def field_path(self) -> str:
        return self._field_path or "multiple"

    def execute(self) -> dict[str, Any]:
        result = {}
        for cmd in self.commands:
            result.update(cmd.execute())
        return result

    def undo(self) -> dict[str, Any]:
        result = {}
        for cmd in reversed(self.commands):
            result.update(cmd.undo())
        return result


@dataclass
class HistoryEntry:
    """Single entry in the command history."""
    command: Command
    timestamp: float = field(default_factory=time.time)
    undone: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.command.field,
            "old_value": self.command.old_value,
            "new_value": self.command.new_value,
            "section": self.command.section,
            "timestamp": self.timestamp,
            "undone": self.undone,
            "description": self.command.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoryEntry:
        cmd = ConfigCommand(
            field=data["field"],
            old_value=data["old_value"],
            new_value=data["new_value"],
            section=data.get("section", ""),
        )
        entry = cls(command=cmd, timestamp=data["timestamp"], undone=data["undone"])
        return entry


class CommandHistory:
    """Manages undo/redo stacks for configuration changes."""

    MAX_HISTORY = 100

    def __init__(self) -> None:
        self._undo_stack: list[HistoryEntry] = []
        self._redo_stack: list[HistoryEntry] = []

    def push(self, command: Command) -> None:
        """Add a command to the undo stack."""
        entry = HistoryEntry(command=command)
        self._undo_stack.append(entry)
        if len(self._undo_stack) > self.MAX_HISTORY:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> Command | None:
        """Pop and return the most recent command for undoing."""
        if not self._undo_stack:
            return None
        entry = self._undo_stack.pop()
        entry.undone = True
        self._redo_stack.append(entry)
        return entry.command

    def redo(self) -> Command | None:
        """Pop and return the most recent undone command for re-executing."""
        if not self._redo_stack:
            return None
        entry = self._redo_stack.pop()
        entry.undone = False
        self._undo_stack.append(entry)
        return entry.command

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def get_history(self) -> list[HistoryEntry]:
        """Return all history entries (oldest first)."""
        return list(reversed(self._undo_stack))

    def get_undo_description(self) -> str | None:
        """Get description of next undo action."""
        if self._undo_stack:
            return self._undo_stack[-1].command.description
        return None

    def get_redo_description(self) -> str | None:
        """Get description of next redo action."""
        if self._redo_stack:
            return self._redo_stack[-1].command.description
        return None

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "undo_stack": [e.to_dict() for e in self._undo_stack],
            "redo_stack": [e.to_dict() for e in self._redo_stack],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CommandHistory:
        history = cls()
        history._undo_stack = [HistoryEntry.from_dict(e) for e in data.get("undo_stack", [])]
        history._redo_stack = [HistoryEntry.from_dict(e) for e in data.get("redo_stack", [])]
        return history

    def save_to_file(self, path: Path) -> None:
        """Persist history to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, path: Path) -> CommandHistory:
        """Load history from a JSON file."""
        if not path.exists():
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))


class HistoryManager:
    """Application-level history manager that persists across sessions."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._history = CommandHistory()
        self._config_path = config_path
        if config_path:
            history_path = config_path.parent / ".history.json"
            self._history_file = history_path
            self._history = CommandHistory.load_from_file(history_path)
        else:
            self._history_file = None

    def record_change(self, field: str, old_value: Any, new_value: Any, section: str = "") -> None:
        """Record a configuration change."""
        cmd = ConfigCommand(field=field, old_value=old_value, new_value=new_value, section=section)
        self._history.push(cmd)
        self._persist()

    def record_batch(self, changes: list[tuple[str, Any, Any]], section: str = "") -> None:
        """Record multiple changes as a single batch command."""
        commands = [
            ConfigCommand(field=f, old_value=o, new_value=n, section=section)
            for f, o, n in changes
        ]
        batch = BatchCommand(commands=commands)
        self._history.push(batch)
        self._persist()

    def undo(self) -> tuple[str, dict[str, Any]] | None:
        """Undo the last change. Returns (field, values) for applying."""
        cmd = self._history.undo()
        if cmd:
            self._persist()
            return cmd.field_path, cmd.undo()
        return None

    def redo(self) -> tuple[str, dict[str, Any]] | None:
        """Redo the last undone change. Returns (field, values) for applying."""
        cmd = self._history.redo()
        if cmd:
            self._persist()
            return cmd.field_path, cmd.execute()
        return None

    def can_undo(self) -> bool:
        return self._history.can_undo()

    def can_redo(self) -> bool:
        return self._history.can_redo()

    def get_history(self) -> list[HistoryEntry]:
        return self._history.get_history()

    def get_undo_description(self) -> str | None:
        return self._history.get_undo_description()

    def get_redo_description(self) -> str | None:
        return self._history.get_redo_description()

    def _persist(self) -> None:
        if self._history_file:
            self._history.save_to_file(self._history_file)

    def clear(self) -> None:
        self._history.clear()
        self._persist()
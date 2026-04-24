"""Unit tests for history module."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.history import (
    BatchCommand,
    CommandHistory,
    ConfigCommand,
    HistoryEntry,
    HistoryManager,
)


class TestConfigCommand:
    def test_execute_returns_new_value(self):
        cmd = ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3")
        result = cmd.execute()
        assert result == {"model": "claude-3"}

    def test_undo_returns_old_value(self):
        cmd = ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3")
        result = cmd.undo()
        assert result == {"model": "gpt-4"}

    def test_description(self):
        cmd = ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3")
        assert cmd.description == "Change model"

    def test_field_path(self):
        cmd = ConfigCommand(field="formatter.executable", old_value="black", new_value="ruff")
        assert cmd.field_path == "formatter.executable"

    def test_with_section(self):
        cmd = ConfigCommand(field="timeout", old_value=30, new_value=60, section="server")
        assert cmd.section == "server"


class TestBatchCommand:
    def test_execute_runs_all_commands(self):
        cmd1 = ConfigCommand(field="a", old_value=1, new_value=2)
        cmd2 = ConfigCommand(field="b", old_value=3, new_value=4)
        batch = BatchCommand(commands=[cmd1, cmd2])
        result = batch.execute()
        assert result == {"a": 2, "b": 4}

    def test_undo_reverses_in_order(self):
        cmd1 = ConfigCommand(field="a", old_value=1, new_value=2)
        cmd2 = ConfigCommand(field="b", old_value=3, new_value=4)
        batch = BatchCommand(commands=[cmd1, cmd2])
        result = batch.undo()
        assert result == {"a": 1, "b": 3}

    def test_description_uses_custom_or_default(self):
        cmd1 = ConfigCommand(field="a", old_value=1, new_value=2)
        batch = BatchCommand(commands=[cmd1], _description="Custom batch")
        assert batch.description == "Custom batch"

    def test_empty_batch(self):
        batch = BatchCommand(commands=[])
        result = batch.execute()
        assert result == {}


class TestHistoryEntry:
    def test_to_dict(self):
        cmd = ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3")
        entry = HistoryEntry(command=cmd, timestamp=1000.0)
        data = entry.to_dict()
        assert data["field"] == "model"
        assert data["old_value"] == "gpt-4"
        assert data["new_value"] == "claude-3"
        assert data["timestamp"] == 1000.0
        assert data["undone"] is False

    def test_from_dict(self):
        data = {
            "field": "timeout",
            "old_value": 30,
            "new_value": 60,
            "section": "server",
            "timestamp": 1000.0,
            "undone": True,
        }
        entry = HistoryEntry.from_dict(data)
        assert entry.command.field == "timeout"
        assert entry.command.old_value == 30
        assert entry.command.new_value == 60
        assert entry.timestamp == 1000.0
        assert entry.undone is True


class TestCommandHistory:
    def test_push_adds_to_undo_stack(self):
        history = CommandHistory()
        cmd = ConfigCommand(field="a", old_value=1, new_value=2)
        history.push(cmd)
        assert len(history._undo_stack) == 1
        assert history.can_undo() is True

    def test_undo_returns_command_and_moves_to_redo(self):
        history = CommandHistory()
        cmd = ConfigCommand(field="a", old_value=1, new_value=2)
        history.push(cmd)
        undone = history.undo()
        assert undone == cmd
        assert len(history._redo_stack) == 1
        assert history.can_redo() is True

    def test_redo_returns_command_and_moves_to_undo(self):
        history = CommandHistory()
        cmd = ConfigCommand(field="a", old_value=1, new_value=2)
        history.push(cmd)
        history.undo()
        redo_cmd = history.redo()
        assert redo_cmd == cmd
        assert len(history._undo_stack) == 1

    def test_undo_when_empty_returns_none(self):
        history = CommandHistory()
        result = history.undo()
        assert result is None

    def test_redo_when_empty_returns_none(self):
        history = CommandHistory()
        result = history.redo()
        assert result is None

    def test_push_clears_redo_stack(self):
        history = CommandHistory()
        cmd1 = ConfigCommand(field="a", old_value=1, new_value=2)
        cmd2 = ConfigCommand(field="b", old_value=3, new_value=4)
        history.push(cmd1)
        history.undo()
        history.push(cmd2)
        assert len(history._redo_stack) == 0

    def test_max_history_limits_size(self):
        history = CommandHistory()
        history.MAX_HISTORY = 3
        for i in range(5):
            history.push(ConfigCommand(field=f"f{i}", old_value=i, new_value=i + 1))
        assert len(history._undo_stack) == 3
        assert history._undo_stack[0].command.field == "f2"

    def test_get_history_returns_reversed(self):
        history = CommandHistory()
        history.push(ConfigCommand(field="a", old_value=1, new_value=2))
        history.push(ConfigCommand(field="b", old_value=3, new_value=4))
        hist = history.get_history()
        assert len(hist) == 2

    def test_get_undo_description(self):
        history = CommandHistory()
        history.push(ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3"))
        desc = history.get_undo_description()
        assert desc == "Change model"

    def test_clear(self):
        history = CommandHistory()
        history.push(ConfigCommand(field="a", old_value=1, new_value=2))
        history.clear()
        assert len(history._undo_stack) == 0
        assert len(history._redo_stack) == 0

    def test_to_dict_and_from_dict(self):
        history = CommandHistory()
        history.push(ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3"))
        data = history.to_dict()
        restored = CommandHistory.from_dict(data)
        assert len(restored._undo_stack) == 1
        assert restored._undo_stack[0].command.field == "model"

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "history.json"
            history = CommandHistory()
            history.push(ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3"))
            history.save_to_file(path)
            loaded = CommandHistory.load_from_file(path)
            assert len(loaded._undo_stack) == 1
            assert loaded._undo_stack[0].command.new_value == "claude-3"

    def test_load_nonexistent_returns_empty(self):
        path = Path("/nonexistent/history.json")
        loaded = CommandHistory.load_from_file(path)
        assert len(loaded._undo_stack) == 0


class TestHistoryManager:
    def test_record_change(self):
        manager = HistoryManager()
        manager.record_change("model", "gpt-4", "claude-3")
        assert manager.can_undo() is True
        assert manager.get_undo_description() == "Change model"

    def test_record_batch(self):
        manager = HistoryManager()
        changes = [
            ("model", "gpt-4", "claude-3"),
            ("timeout", 30, 60),
        ]
        manager.record_batch(changes)
        assert manager.can_undo() is True

    def test_undo_returns_correct_values(self):
        manager = HistoryManager()
        manager.record_change("model", "gpt-4", "claude-3")
        result = manager.undo()
        assert result is not None
        field, values = result
        assert field == "model"
        assert values == {"model": "gpt-4"}

    def test_redo_returns_correct_values(self):
        manager = HistoryManager()
        manager.record_change("model", "gpt-4", "claude-3")
        manager.undo()
        result = manager.redo()
        assert result is not None
        field, values = result
        assert field == "model"
        assert values == {"model": "claude-3"}

    def test_persistence(self, tmp_path):
        config_path = tmp_path / "config.json"
        config_path.write_text("{}")
        manager = HistoryManager(config_path=config_path)
        manager.record_change("model", "gpt-4", "claude-3")
        manager2 = HistoryManager(config_path=config_path)
        assert manager2.can_undo() is True
        assert manager2.get_undo_description() == "Change model"

    def test_clear(self, tmp_path):
        config_path = tmp_path / "config.json"
        config_path.write_text("{}")
        manager = HistoryManager(config_path=config_path)
        manager.record_change("model", "gpt-4", "claude-3")
        manager.clear()
        assert manager.can_undo() is False
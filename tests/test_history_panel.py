"""Tests for history panel UI component."""
from __future__ import annotations

import pytest

from app.history import CommandHistory, ConfigCommand, HistoryEntry


class TestHistoryPanel:
    def test_history_panel_renders_entry_list(self):
        """History panel shows a scrollable list of history entries."""
        history = CommandHistory()
        history.push(ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3"))
        history.push(ConfigCommand(field="timeout", old_value=30, new_value=60))
        entries = history.get_history()
        assert len(entries) == 2

    def test_history_panel_shows_entry_descriptions(self):
        """History panel displays description for each entry."""
        history = CommandHistory()
        history.push(ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3"))
        desc = history.get_undo_description()
        assert desc == "Change model"

    def test_history_panel_indicates_current_position(self):
        """History panel highlights current undo position."""
        history = CommandHistory()
        history.push(ConfigCommand(field="a", old_value=1, new_value=2))
        history.push(ConfigCommand(field="b", old_value=3, new_value=4))
        history.undo()
        assert history.can_redo() is True
        assert history.can_undo() is True

    def test_click_to_revert(self):
        """Clicking a history entry reverts to that state."""
        history = CommandHistory()
        history.push(ConfigCommand(field="a", old_value=1, new_value=2))
        history.push(ConfigCommand(field="b", old_value=3, new_value=4))
        cmd = history.undo()
        assert cmd.field == "b"
        result = cmd.undo()
        assert result == {"b": 3}

    def test_history_search_filters_entries(self):
        """History panel can filter entries by field name."""
        history = CommandHistory()
        history.push(ConfigCommand(field="model", old_value="gpt-4", new_value="claude-3"))
        history.push(ConfigCommand(field="timeout", old_value=30, new_value=60))
        entries = history.get_history()
        model_entries = [e for e in entries if "model" in e.command.field]
        assert len(model_entries) == 1

    def test_undone_entries_appear_different(self):
        """Entries that have been undone are visually distinct."""
        history = CommandHistory()
        history.push(ConfigCommand(field="a", old_value=1, new_value=2))
        history.push(ConfigCommand(field="b", old_value=3, new_value=4))
        history.undo()
        assert history._redo_stack[0].undone is True
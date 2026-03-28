"""Tests for reusable GUI widgets."""

import tkinter as tk

import pytest

from app.config_schema import FieldDef, FieldType
from app.widgets import (
    ColorPicker,
    DynamicDictEditor,
    DynamicDictModal,
    KeyValueEditor,
    LabeledCheck,
    LabeledCombo,
    LabeledEntry,
    LabeledSlider,
    LabeledSpinbox,
    LabeledStringOrBool,
    LabeledSuggest,
    MultilineText,
    ObjectEditor,
    PermissionRow,
    RadioGroup,
    SearchableCombo,
    StringListEditor,
    build_field_widget,
)


@pytest.fixture
def tk_root() -> tk.Tk:
    """Create a Tk root window for widget tests.

    Skips tests when no display server is available.
    """
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    root.withdraw()
    yield root
    root.destroy()


def test_build_field_widget_selects_expected_class(tk_root: tk.Tk) -> None:
    bool_def = FieldDef("snapshot", FieldType.BOOLEAN, "desc")
    enum_def = FieldDef(
        "share", FieldType.ENUM, "desc", enum_values=["manual", "auto"]
    )
    list_def = FieldDef("cors", FieldType.STRING_LIST, "desc")
    obj_def = FieldDef("environment", FieldType.OBJECT, "desc")
    suggest_def = FieldDef(
        "theme",
        FieldType.STRING,
        "desc",
        suggestions=["tokyonight", "nord"],
    )
    sob_def = FieldDef("autoupdate", FieldType.STRING_OR_BOOL, "desc")
    str_def = FieldDef("model", FieldType.STRING, "desc")

    assert isinstance(build_field_widget(tk_root, bool_def), LabeledCheck)
    assert isinstance(build_field_widget(tk_root, enum_def), RadioGroup)  # ≤5 values → RadioGroup
    assert isinstance(build_field_widget(tk_root, list_def), StringListEditor)
    assert isinstance(build_field_widget(tk_root, obj_def), ObjectEditor)
    assert isinstance(build_field_widget(tk_root, suggest_def), LabeledSuggest)
    assert isinstance(build_field_widget(tk_root, sob_def), LabeledStringOrBool)
    assert isinstance(build_field_widget(tk_root, str_def), LabeledEntry)


def test_labeled_entry_and_check_get_set_value(tk_root: tk.Tk) -> None:
    entry_def = FieldDef("model", FieldType.STRING, "Model")
    entry = LabeledEntry(tk_root, entry_def)

    assert entry.get_value() is None
    entry.set_value("openai/gpt-4.1")
    assert entry.get_value() == "openai/gpt-4.1"
    entry.set_value("   ")
    assert entry.get_value() is None

    check_def = FieldDef("snapshot", FieldType.BOOLEAN, "Snapshot", default=True)
    check = LabeledCheck(tk_root, check_def)

    assert check.get_value() is None
    check.set_value(True)
    assert check.get_value() is True
    check.set_value(None)
    assert check.get_value() is None


def test_string_list_editor_add_and_remove(tk_root: tk.Tk) -> None:
    field = FieldDef("cors", FieldType.STRING_LIST, "Allowed origins")
    editor = StringListEditor(tk_root, field)

    editor.add_var.set("https://example.com")
    editor._add_item()
    editor.add_var.set("https://api.example.com")
    editor._add_item()

    assert editor.get_value() == ["https://example.com", "https://api.example.com"]

    editor.listbox.selection_set(0)
    editor._remove_item()
    assert editor.get_value() == ["https://api.example.com"]


def test_permission_row_set_and_get(tk_root: tk.Tk) -> None:
    row = PermissionRow(tk_root, "bash")
    assert row.get_value() is None

    row.set_value("ask")
    assert row.get_value() == "ask"

    row.set_value("")
    assert row.get_value() is None


def test_object_editor_set_and_get(tk_root: tk.Tk) -> None:
    field = FieldDef("environment", FieldType.OBJECT, "Environment values")
    editor = ObjectEditor(tk_root, field)

    assert editor.get_value() is None
    editor.set_value({"PYTHONPATH": ".", "DEBUG": "1"})
    assert editor.get_value() == {"PYTHONPATH": ".", "DEBUG": "1"}

    editor.var.set("not json")
    assert editor.get_value() is None


def test_string_or_bool_widget_values(tk_root: tk.Tk) -> None:
    field = FieldDef("autoupdate", FieldType.STRING_OR_BOOL, "Auto updates")
    widget = LabeledStringOrBool(tk_root, field)

    assert widget.get_value() is None
    widget.set_value(True)
    assert widget.get_value() == "true"
    widget.set_value(False)
    assert widget.get_value() == "false"
    widget.set_value("notify")
    assert widget.get_value() == "notify"


def test_dynamic_dict_editor_load_select_and_save(tk_root: tk.Tk) -> None:
    fields = [
        FieldDef("npm", FieldType.STRING, "pkg"),
        FieldDef("options.timeout", FieldType.INTEGER, "timeout"),
        FieldDef("options.setCacheKey", FieldType.BOOLEAN, "cache key"),
    ]
    editor = DynamicDictEditor(tk_root, "providers", fields)

    editor.set_value(
        {
            "openai": {
                "npm": "provider-openai",
                "options": {"timeout": 300000, "setCacheKey": True},
            }
        }
    )

    editor.key_listbox.selection_set(0)
    editor._on_select(None)
    editor.widgets["options.timeout"].set_value("120000")
    editor.widgets["options.setCacheKey"].set_value(False)
    editor._save_current()

    value = editor.get_value()
    assert value is not None
    assert value["openai"]["options"]["timeout"] == "120000"
    assert value["openai"]["options"]["setCacheKey"] is False


def test_radio_group_get_set(tk_root: tk.Tk) -> None:
    field = FieldDef(
        "share", FieldType.ENUM, "Share mode",
        enum_values=["manual", "auto", "disabled"],
    )
    radio = RadioGroup(tk_root, field)
    assert radio.get_value() is None
    radio.set_value("auto")
    assert radio.get_value() == "auto"
    radio.set_value(None)
    assert radio.get_value() is None


def test_labeled_spinbox_get_set(tk_root: tk.Tk) -> None:
    field = FieldDef(
        "port", FieldType.INTEGER, "Port",
        min_value=0, max_value=65535, default=0,
    )
    spinbox = LabeledSpinbox(tk_root, field)
    assert spinbox.get_value() is None
    spinbox.set_value(8080)
    assert spinbox.get_value() == 8080
    spinbox.set_value(None)
    assert spinbox.get_value() is None


def test_labeled_slider_get_set(tk_root: tk.Tk) -> None:
    field = FieldDef(
        "temperature", FieldType.NUMBER, "Temperature",
        min_value=0, max_value=1,
    )
    slider = LabeledSlider(tk_root, field)
    slider.set_value(0.7)
    val = slider.get_value()
    assert val is not None
    assert abs(val - 0.7) < 0.02  # slider resolution
    slider.set_value(None)
    assert slider.get_value() is None


def test_color_picker_get_set(tk_root: tk.Tk) -> None:
    field = FieldDef(
        "color", FieldType.ENUM, "Agent color",
        enum_values=["primary", "secondary", "accent",
                     "success", "warning", "error", "info"],
    )
    picker = ColorPicker(tk_root, field)
    assert picker.get_value() is None
    picker.set_value("primary")
    assert picker.get_value() == "primary"
    picker.set_value("#ff0000")
    assert picker.get_value() == "#ff0000"


def test_key_value_editor_get_set(tk_root: tk.Tk) -> None:
    field = FieldDef("environment", FieldType.KEY_VALUE_MAP, "Env vars")
    editor = KeyValueEditor(tk_root, field)
    assert editor.get_value() is None
    editor.set_value({"PATH": "/usr/bin", "HOME": "/root"})
    result = editor.get_value()
    assert result == {"PATH": "/usr/bin", "HOME": "/root"}


def test_multiline_text_get_set(tk_root: tk.Tk) -> None:
    field = FieldDef("prompt", FieldType.STRING, "System prompt")
    ml = MultilineText(tk_root, field)
    assert ml.get_value() is None
    ml.set_value("Hello\nWorld")
    assert ml.get_value() == "Hello\nWorld"
    ml.set_value(None)
    assert ml.get_value() is None


def test_searchable_combo_get_set(tk_root: tk.Tk) -> None:
    field = FieldDef(
        "model", FieldType.STRING, "Model",
        suggestions=["openai/gpt-4.1", "anthropic/claude-sonnet-4-6", "google/gemini-2.5-pro"],
    )
    combo = SearchableCombo(tk_root, field)
    assert combo.get_value() is None
    combo.set_value("openai/gpt-4.1")
    assert combo.get_value() == "openai/gpt-4.1"


def test_build_field_widget_routes_new_types(tk_root: tk.Tk) -> None:
    # KEY_VALUE_MAP → KeyValueEditor
    kv_def = FieldDef("env", FieldType.KEY_VALUE_MAP, "desc")
    assert isinstance(build_field_widget(tk_root, kv_def), KeyValueEditor)

    # INTEGER with min/max → LabeledSpinbox
    int_def = FieldDef("port", FieldType.INTEGER, "desc", min_value=0, max_value=65535)
    assert isinstance(build_field_widget(tk_root, int_def), LabeledSpinbox)

    # NUMBER with 0-1 range → LabeledSlider
    slider_def = FieldDef("temperature", FieldType.NUMBER, "desc", min_value=0, max_value=1)
    assert isinstance(build_field_widget(tk_root, slider_def), LabeledSlider)


def test_dynamic_dict_modal_ok(tk_root: tk.Tk) -> None:
    fields = [
        FieldDef("name", FieldType.STRING, "Name"),
        FieldDef("enabled", FieldType.BOOLEAN, "Enabled"),
    ]
    modal = DynamicDictModal(
        tk_root, "Add Entry", fields,
        entry_name="test-entry",
        entry_data={"name": "hello", "enabled": True},
    )
    # Verify pre-populated values
    assert modal.widgets["name"].get_value() == "hello"
    # Simulate OK
    modal._on_ok()
    assert modal.result is not None
    assert modal.result_name == "test-entry"
    assert modal.result["name"] == "hello"


def test_dynamic_dict_modal_cancel(tk_root: tk.Tk) -> None:
    fields = [FieldDef("url", FieldType.STRING, "URL")]
    modal = DynamicDictModal(tk_root, "Test", fields, entry_name="x")
    modal._on_cancel()
    assert modal.result is None


def test_dynamic_dict_editor_has_edit_button(tk_root: tk.Tk) -> None:
    fields = [FieldDef("value", FieldType.STRING, "desc")]
    editor = DynamicDictEditor(tk_root, "Test", fields)
    # Verify the editor has an edit button (part of Phase 5)
    assert hasattr(editor, '_edit_key')

"""Tests for schema helpers and validation."""

from app.config_schema import (
    AGENT_ENTRY_FIELDS,
    COMMAND_ENTRY_FIELDS,
    ENTERPRISE_FIELDS,
    EXPERIMENTAL_FIELDS,
    FORMATTER_ENTRY_FIELDS,
    KEYBIND_DEFAULTS,
    KEYBIND_SLOTS,
    LSP_ENTRY_FIELDS,
    MCP_LOCAL_FIELDS,
    MCP_REMOTE_FIELDS,
    PERMISSION_ACTION_ONLY_TOOLS,
    PERMISSION_RULE_TOOLS,
    PERMISSION_TOOLS,
    PROVIDER_ENTRY_FIELDS,
    TUI_FIELDS,
    WELL_KNOWN_AGENTS,
    FieldDef,
    FieldType,
    get_nested,
    remove_nested,
    set_nested,
    validate_config,
    validate_field,
)


def test_validate_field_integer_bounds() -> None:
    field = FieldDef(
        key="port",
        field_type=FieldType.INTEGER,
        description="Port",
        min_value=1,
        max_value=65535,
    )
    assert validate_field(field, "8080") is None
    assert "must be >=" in validate_field(field, 0)
    assert "must be <=" in validate_field(field, 70000)
    assert "must be an integer" in validate_field(field, "abc")


def test_validate_field_enum_and_required() -> None:
    field = FieldDef(
        key="share",
        field_type=FieldType.ENUM,
        description="Share mode",
        enum_values=["manual", "auto", "disabled"],
        required=True,
    )
    assert validate_field(field, "auto") is None
    assert "required" in validate_field(field, "")
    assert "must be one of" in validate_field(field, "sometimes")


def test_validate_field_boolean_and_number() -> None:
    bool_field = FieldDef(
        key="snapshot",
        field_type=FieldType.BOOLEAN,
        description="Snapshot",
    )
    assert validate_field(bool_field, True) is None
    assert "must be a boolean" in validate_field(bool_field, "true")

    number_field = FieldDef(
        key="scroll_speed",
        field_type=FieldType.NUMBER,
        description="Scroll speed",
        min_value=0.001,
    )
    assert validate_field(number_field, 1.5) is None
    assert "must be >=" in validate_field(number_field, 0)
    assert "must be a number" in validate_field(number_field, "abc")


def test_permission_tools_has_todowrite() -> None:
    """1.1 — PERMISSION_TOOLS includes todowrite and has 16 entries."""
    assert "todowrite" in PERMISSION_TOOLS
    assert len(PERMISSION_TOOLS) == 16
    # question and todowrite are action-only
    assert "question" in PERMISSION_ACTION_ONLY_TOOLS
    assert "todowrite" in PERMISSION_ACTION_ONLY_TOOLS
    # Other tools accept rules
    assert "read" in PERMISSION_RULE_TOOLS
    assert "bash" in PERMISSION_RULE_TOOLS


def test_mcp_discriminated_union() -> None:
    """1.2 — MCP split into local/remote with correct fields."""
    local_keys = {f.key for f in MCP_LOCAL_FIELDS}
    assert local_keys == {"type", "command", "environment", "enabled", "timeout"}
    # command should be STRING_LIST
    cmd = next(f for f in MCP_LOCAL_FIELDS if f.key == "command")
    assert cmd.field_type == FieldType.STRING_LIST

    remote_keys = {f.key for f in MCP_REMOTE_FIELDS}
    assert remote_keys == {"type", "url", "enabled", "headers", "oauth", "timeout"}


def test_provider_entry_fields_corrected() -> None:
    """1.3 — Provider fields: no npm/name, has options.apiKey etc."""
    keys = {f.key for f in PROVIDER_ENTRY_FIELDS}
    assert "npm" not in keys
    assert "name" not in keys
    assert "options.apiKey" in keys
    assert "options.baseURL" in keys
    assert "options.enterpriseUrl" in keys
    assert "options.setCacheKey" in keys
    assert "options.timeout" in keys
    assert "options.chunkTimeout" in keys
    assert "whitelist" in keys
    assert "blacklist" in keys
    assert "models" in keys
    assert "disabled" in keys


def test_agent_entry_fields_updated() -> None:
    """1.4 — Agent fields include variant, permission, options, color enum."""
    keys = {f.key for f in AGENT_ENTRY_FIELDS}
    assert "variant" in keys
    assert "permission" in keys
    assert "options" in keys
    color_field = next(f for f in AGENT_ENTRY_FIELDS if f.key == "color")
    assert "primary" in color_field.enum_values
    assert "error" in color_field.enum_values


def test_formatter_command_is_string_list() -> None:
    """1.5 — Formatter command is STRING_LIST."""
    cmd = next(f for f in FORMATTER_ENTRY_FIELDS if f.key == "command")
    assert cmd.field_type == FieldType.STRING_LIST


def test_command_entry_has_subtask_and_model() -> None:
    """1.6 — Command entry has subtask boolean and model field."""
    keys = {f.key for f in COMMAND_ENTRY_FIELDS}
    assert "subtask" in keys
    assert "model" in keys
    subtask = next(f for f in COMMAND_ENTRY_FIELDS if f.key == "subtask")
    assert subtask.field_type == FieldType.BOOLEAN


def test_lsp_entry_fields_exist() -> None:
    """1.7 — LSP entry fields exist with correct types."""
    keys = {f.key for f in LSP_ENTRY_FIELDS}
    assert keys == {"command", "extensions", "disabled", "env", "initialization"}
    cmd = next(f for f in LSP_ENTRY_FIELDS if f.key == "command")
    assert cmd.field_type == FieldType.STRING_LIST


def test_experimental_fields_exist() -> None:
    """1.8 — Experimental fields present."""
    keys = {f.key for f in EXPERIMENTAL_FIELDS}
    assert "disable_paste_summary" in keys
    assert "batch_tool" in keys
    assert "openTelemetry" in keys
    assert "primary_tools" in keys
    assert "continue_loop_on_deny" in keys
    assert "mcp_timeout" in keys


def test_enterprise_fields_exist() -> None:
    """1.9 — Enterprise fields present."""
    keys = {f.key for f in ENTERPRISE_FIELDS}
    assert "url" in keys


def test_well_known_agents() -> None:
    """1.10 — Well-known agent names constant."""
    assert WELL_KNOWN_AGENTS == [
        "build", "plan", "general", "explore",
        "title", "summary", "compaction",
    ]


def test_keybind_slots_has_plugin_manager() -> None:
    """1.11 — plugin_manager slot exists and KEYBIND_DEFAULTS populated."""
    assert "plugin_manager" in KEYBIND_SLOTS
    assert KEYBIND_DEFAULTS["leader"] == "ctrl+x"
    assert KEYBIND_DEFAULTS["app_exit"] == "ctrl+c,ctrl+d,<leader>q"
    assert KEYBIND_DEFAULTS["plugin_manager"] == "none"
    # Every slot has a default
    for slot in KEYBIND_SLOTS:
        assert slot in KEYBIND_DEFAULTS, f"Missing default for {slot}"


def test_tui_plugin_fields() -> None:
    """1.12 — TUI has plugin and plugin_enabled fields."""
    keys = {f.key for f in TUI_FIELDS}
    assert "plugin" in keys
    assert "plugin_enabled" in keys
    # theme is STRING (not ENUM)
    theme = next(f for f in TUI_FIELDS if f.key == "theme")
    assert theme.field_type == FieldType.STRING


def test_nested_dict_helpers() -> None:
    data: dict = {}
    set_nested(data, "server.port", 4096)
    set_nested(data, "server.hostname", "127.0.0.1")
    assert get_nested(data, "server.port") == 4096
    assert get_nested(data, "server.hostname") == "127.0.0.1"
    assert get_nested(data, "server.missing") is None

    remove_nested(data, "server.port")
    assert get_nested(data, "server.port") is None


def test_validate_config_empty_is_valid() -> None:
    assert validate_config({}) == []


def test_validate_config_general_invalid_enum() -> None:
    data = {"logLevel": "INVALID"}
    errors = validate_config(data)
    assert any("logLevel" in e and "must be one of" in e for e in errors)


def test_validate_config_server_port_out_of_range() -> None:
    data = {"server": {"port": 99999}}
    errors = validate_config(data)
    assert any("port" in e and "<=" in e for e in errors)


def test_validate_config_valid_minimal() -> None:
    data = {
        "$schema": "https://opencode.ai/config.json",
        "model": "test/model",
        "logLevel": "INFO",
        "share": "manual",
        "server": {"port": 8080},
        "snapshot": True,
    }
    assert validate_config(data) == []


def test_validate_config_unknown_permission_tool() -> None:
    data = {"permission": {"unknown_tool_xyz": "allow"}}
    errors = validate_config(data)
    assert any("unknown_tool_xyz" in e for e in errors)


def test_validate_config_provider_valid() -> None:
    data = {
        "provider": {
            "my_provider": {
                "options": {"apiKey": "sk-test"},
                "options": {"baseURL": "https://api.test.com"},
            }
        }
    }
    assert validate_config(data) == []


def test_validate_config_agent_color_enum() -> None:
    data = {
        "agent": {
            "test": {
                "color": "invalid_color",
            }
        }
    }
    errors = validate_config(data)
    assert any("color" in e and "must be one of" in e for e in errors)


def test_validate_config_mcp_local_command_string_list() -> None:
    data = {
        "mcp": {
            "local_mcp": {
                "type": "local",
                "command": "npx",
                "args": ["-y"],
            }
        }
    }
    errors = validate_config(data)
    assert any("command" in e for e in errors)


def test_validate_config_mcp_remote() -> None:
    data = {
        "mcp": {
            "remote_mcp": {
                "type": "remote",
                "url": "https://example.com/mcp",
            }
        }
    }
    assert validate_config(data) == []


def test_validate_config_experimental_fields() -> None:
    data = {
        "experimental": {
            "disable_paste_summary": True,
            "mcp_timeout": 30000,
        }
    }
    assert validate_config(data) == []


def test_validate_config_enterprise_url() -> None:
    data = {"enterprise": {"url": "https://enterprise.example.com"}}
    assert validate_config(data) == []


def test_validate_config_lsp_valid() -> None:
    data = {
        "lsp": {
            "pyright": {
                "command": ["npx", "pyright"],
                "extensions": [".py"],
            }
        }
    }
    assert validate_config(data) == []

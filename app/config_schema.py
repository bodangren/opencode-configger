"""Schema definitions for all OpenCode configuration keys.

Each schema entry defines: key, type, default, description, enum values,
and any constraints needed for validation and form generation.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FieldType(Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"
    STRING_LIST = "string_list"
    STRING_OR_BOOL = "string_or_bool"
    OBJECT = "object"
    KEY_VALUE_MAP = "key_value_map"


@dataclass
class FieldDef:
    """Definition of a single config field."""

    key: str
    field_type: FieldType
    description: str
    default: Any = None
    enum_values: list[str] = field(default_factory=list)
    min_value: float | None = None
    max_value: float | None = None
    required: bool = False
    pattern: str | None = None
    parent: str = ""  # dot-separated parent path, e.g. "server"
    suggestions: list[str] = field(default_factory=list)

    @property
    def full_key(self) -> str:
        if self.parent:
            return f"{self.parent}.{self.key}"
        return self.key


# ─── General Settings ───────────────────────────────────────────────

GENERAL_FIELDS: list[FieldDef] = [
    FieldDef(
        key="model",
        field_type=FieldType.STRING,
        description="Primary LLM model (format: provider/model)",
    ),
    FieldDef(
        key="small_model",
        field_type=FieldType.STRING,
        description="Lightweight model for tasks like title generation",
    ),
    FieldDef(
        key="default_agent",
        field_type=FieldType.STRING,
        description="Default agent to use when unspecified",
        suggestions=["build", "plan", "general", "explore",
                      "title", "summary", "compaction"],
    ),
    FieldDef(
        key="logLevel",
        field_type=FieldType.ENUM,
        description="Logging verbosity level",
        enum_values=["DEBUG", "INFO", "WARN", "ERROR"],
    ),
    FieldDef(
        key="username",
        field_type=FieldType.STRING,
        description="Display name for the user",
    ),
    FieldDef(
        key="share",
        field_type=FieldType.ENUM,
        description="Session sharing mode",
        default="manual",
        enum_values=["manual", "auto", "disabled"],
    ),
    FieldDef(
        key="autoupdate",
        field_type=FieldType.STRING_OR_BOOL,
        description='Auto-update behavior (true, false, or "notify")',
        default=True,
        suggestions=["true", "false", "notify"],
    ),
    FieldDef(
        key="snapshot",
        field_type=FieldType.BOOLEAN,
        description="Enable change tracking via internal git",
        default=True,
    ),
]

# ─── Server Settings ────────────────────────────────────────────────

SERVER_FIELDS: list[FieldDef] = [
    FieldDef(
        key="port",
        field_type=FieldType.INTEGER,
        description="Listen port (0 = auto)",
        default=0,
        min_value=0,
        max_value=65535,
        parent="server",
    ),
    FieldDef(
        key="hostname",
        field_type=FieldType.STRING,
        description="Listen address",
        default="127.0.0.1",
        parent="server",
    ),
    FieldDef(
        key="mdns",
        field_type=FieldType.BOOLEAN,
        description="Enable mDNS service discovery",
        default=False,
        parent="server",
    ),
    FieldDef(
        key="mdnsDomain",
        field_type=FieldType.STRING,
        description="Custom domain for mDNS service",
        default="opencode.local",
        parent="server",
    ),
    FieldDef(
        key="cors",
        field_type=FieldType.STRING_LIST,
        description="Allowed CORS origins (full URLs)",
        parent="server",
    ),
]

# ─── Compaction Settings ────────────────────────────────────────────

COMPACTION_FIELDS: list[FieldDef] = [
    FieldDef(
        key="auto",
        field_type=FieldType.BOOLEAN,
        description="Auto-compact context when full",
        default=True,
        parent="compaction",
    ),
    FieldDef(
        key="prune",
        field_type=FieldType.BOOLEAN,
        description="Remove old outputs during compaction",
        default=True,
        parent="compaction",
    ),
    FieldDef(
        key="reserved",
        field_type=FieldType.INTEGER,
        description="Token buffer reserved during compaction",
        parent="compaction",
    ),
]

# ─── Watcher & Instructions ────────────────────────────────────────

WATCHER_FIELDS: list[FieldDef] = [
    FieldDef(
        key="ignore",
        field_type=FieldType.STRING_LIST,
        description="Glob patterns to exclude from file watching",
        parent="watcher",
    ),
]

INSTRUCTIONS_FIELDS: list[FieldDef] = [
    FieldDef(
        key="instructions",
        field_type=FieldType.STRING_LIST,
        description="Paths or globs to instruction files",
    ),
]

PLUGIN_FIELDS: list[FieldDef] = [
    FieldDef(
        key="plugin",
        field_type=FieldType.STRING_LIST,
        description="npm plugin identifiers",
    ),
]

SKILLS_FIELDS: list[FieldDef] = [
    FieldDef(
        key="paths",
        field_type=FieldType.STRING_LIST,
        description="Local skill directory paths",
        parent="skills",
    ),
    FieldDef(
        key="urls",
        field_type=FieldType.STRING_LIST,
        description="Remote skill URLs",
        parent="skills",
    ),
]

PROVIDER_LIST_FIELDS: list[FieldDef] = [
    FieldDef(
        key="disabled_providers",
        field_type=FieldType.STRING_LIST,
        description="Provider IDs to exclude (takes priority over enabled)",
    ),
    FieldDef(
        key="enabled_providers",
        field_type=FieldType.STRING_LIST,
        description="Allowlisted provider IDs",
    ),
]

# ─── Permission (Tools) ────────────────────────────────────────────

PERMISSION_TOOLS: list[str] = [
    "read", "edit", "glob", "grep", "list", "bash", "task",
    "external_directory", "question", "todowrite", "webfetch", "websearch",
    "codesearch", "lsp", "skill", "doom_loop",
]

# Tools that accept only PermissionAction (flat enum: allow/ask/deny)
PERMISSION_ACTION_ONLY_TOOLS: list[str] = ["question", "todowrite"]

# Tools that accept PermissionRule (flat enum OR pattern-record)
PERMISSION_RULE_TOOLS: list[str] = [
    "read", "edit", "glob", "grep", "list", "bash", "task",
    "external_directory", "webfetch", "websearch",
    "codesearch", "lsp", "skill", "doom_loop",
]

PERMISSION_VALUES: list[str] = ["allow", "ask", "deny"]

# ─── Provider Entry Fields ──────────────────────────────────────────

PROVIDER_ENTRY_FIELDS: list[FieldDef] = [
    FieldDef(key="options.apiKey", field_type=FieldType.STRING,
             description="API key"),
    FieldDef(key="options.baseURL", field_type=FieldType.STRING,
             description="Custom API endpoint"),
    FieldDef(key="options.enterpriseUrl", field_type=FieldType.STRING,
             description="GitHub Enterprise URL (copilot)"),
    FieldDef(key="options.setCacheKey", field_type=FieldType.BOOLEAN,
             description="Enable promptCacheKey"),
    FieldDef(key="options.timeout", field_type=FieldType.INTEGER,
             description="Request timeout ms (default 300000, false to disable)",
             default=300000),
    FieldDef(key="options.chunkTimeout", field_type=FieldType.INTEGER,
             description="SSE chunk timeout (ms)", min_value=1),
    FieldDef(key="whitelist", field_type=FieldType.STRING_LIST,
             description="Allowed model IDs"),
    FieldDef(key="blacklist", field_type=FieldType.STRING_LIST,
             description="Blocked model IDs"),
    FieldDef(key="models", field_type=FieldType.OBJECT,
             description="Per-model config overrides and variant settings"),
    FieldDef(key="disabled", field_type=FieldType.BOOLEAN,
             description="Disable provider entirely"),
]

# ─── Agent Entry Fields ─────────────────────────────────────────────

AGENT_ENTRY_FIELDS: list[FieldDef] = [
    FieldDef(key="model", field_type=FieldType.STRING,
             description="Model reference (provider/model)"),
    FieldDef(key="prompt", field_type=FieldType.STRING,
             description="System prompt for the agent"),
    FieldDef(key="description", field_type=FieldType.STRING,
             description="Agent description"),
    FieldDef(key="variant", field_type=FieldType.STRING,
             description="Agent variant identifier"),
    FieldDef(key="mode", field_type=FieldType.ENUM,
             description="Agent mode",
             enum_values=["subagent", "primary", "all"]),
    FieldDef(key="hidden", field_type=FieldType.BOOLEAN,
             description="Hide agent from UI"),
    FieldDef(key="disable", field_type=FieldType.BOOLEAN,
             description="Disable the agent"),
    FieldDef(key="color", field_type=FieldType.ENUM,
             description="Theme color for the agent",
             enum_values=["primary", "secondary", "accent",
                          "success", "warning", "error", "info"]),
    FieldDef(key="steps", field_type=FieldType.INTEGER,
             description="Maximum steps (maxSteps is deprecated alias)",
             min_value=1),
    FieldDef(key="temperature", field_type=FieldType.NUMBER,
             description="Sampling temperature"),
    FieldDef(key="top_p", field_type=FieldType.NUMBER,
             description="Top-p sampling parameter"),
    FieldDef(key="permission", field_type=FieldType.OBJECT,
             description="Permission overrides for this agent"),
    FieldDef(key="options", field_type=FieldType.OBJECT,
             description="Additional agent options"),
]

# ─── Command Entry Fields ───────────────────────────────────────────

COMMAND_ENTRY_FIELDS: list[FieldDef] = [
    FieldDef(key="template", field_type=FieldType.STRING,
             description="Command template (required)", required=True),
    FieldDef(key="description", field_type=FieldType.STRING,
             description="Command description"),
    FieldDef(key="agent", field_type=FieldType.STRING,
             description="Agent to use for this command"),
    FieldDef(key="model", field_type=FieldType.STRING,
             description="Model to use for this command"),
    FieldDef(key="subtask", field_type=FieldType.BOOLEAN,
             description="Run command as a subtask"),
]

# ─── Formatter Entry Fields ─────────────────────────────────────────

FORMATTER_ENTRY_FIELDS: list[FieldDef] = [
    FieldDef(key="disabled", field_type=FieldType.BOOLEAN,
             description="Disable this formatter"),
    FieldDef(key="command", field_type=FieldType.STRING_LIST,
             description="Formatter command to execute (array)"),
    FieldDef(key="extensions", field_type=FieldType.STRING_LIST,
             description="File extensions to format"),
    FieldDef(key="environment", field_type=FieldType.KEY_VALUE_MAP,
             description="Environment variables as key/value pairs"),
]

# ─── MCP Entry Fields (discriminated union on type) ─────────────────

MCP_LOCAL_FIELDS: list[FieldDef] = [
    FieldDef(key="type", field_type=FieldType.ENUM,
             description="Connection type", enum_values=["local"]),
    FieldDef(key="command", field_type=FieldType.STRING_LIST,
             description="Command and args combined in one array"),
    FieldDef(key="environment", field_type=FieldType.KEY_VALUE_MAP,
             description="Environment variables for the server"),
    FieldDef(key="enabled", field_type=FieldType.BOOLEAN,
             description="Enable on startup"),
    FieldDef(key="timeout", field_type=FieldType.INTEGER,
             description="Request timeout (ms)", default=5000, min_value=1),
]

MCP_REMOTE_FIELDS: list[FieldDef] = [
    FieldDef(key="type", field_type=FieldType.ENUM,
             description="Connection type", enum_values=["remote"]),
    FieldDef(key="url", field_type=FieldType.STRING,
             description="Server URL"),
    FieldDef(key="enabled", field_type=FieldType.BOOLEAN,
             description="Enable on startup"),
    FieldDef(key="headers", field_type=FieldType.KEY_VALUE_MAP,
             description="HTTP headers"),
    FieldDef(key="oauth", field_type=FieldType.OBJECT,
             description="OAuth config (clientId, clientSecret, scope) or false"),
    FieldDef(key="timeout", field_type=FieldType.INTEGER,
             description="Request timeout (ms)", default=5000, min_value=1),
]

# Backward-compat alias for code that still references the flat list
MCP_ENTRY_FIELDS: list[FieldDef] = MCP_LOCAL_FIELDS

# ─── TUI Settings ──────────────────────────────────────────────────

TUI_FIELDS: list[FieldDef] = [
    FieldDef(
        key="theme",
        field_type=FieldType.STRING,
        description="UI theme identifier (e.g., 'tokyonight')",
        suggestions=[
            "opencode",
            "tokyonight",
            "catppuccin",
            "nord",
            "solarized-dark",
            "solarized-light",
            "dracula",
            "github-dark",
            "github-light",
            "gruvbox-dark",
            "gruvbox-light",
        ],
    ),
    FieldDef(
        key="scroll_speed",
        field_type=FieldType.NUMBER,
        description="Scroll velocity",
        min_value=0.001,
    ),
    FieldDef(
        key="diff_style",
        field_type=FieldType.ENUM,
        description="Diff rendering style",
        enum_values=["auto", "stacked"],
    ),
    FieldDef(
        key="plugin",
        field_type=FieldType.STRING_LIST,
        description="TUI plugin identifiers (same PluginSpec format as main config)",
    ),
    FieldDef(
        key="plugin_enabled",
        field_type=FieldType.OBJECT,
        description="Toggle individual plugins (Record<string, boolean>)",
    ),
]

TUI_SCROLL_ACCEL_FIELDS: list[FieldDef] = [
    FieldDef(
        key="enabled",
        field_type=FieldType.BOOLEAN,
        description="Enable scroll acceleration",
        parent="scroll_acceleration",
    ),
]

# ─── Keybinding Slots ──────────────────────────────────────────────

KEYBIND_SLOTS: list[str] = [
    "leader", "app_exit", "editor_open", "theme_list",
    "sidebar_toggle", "scrollbar_toggle", "username_toggle",
    "status_view", "session_export", "session_new", "session_list",
    "session_timeline", "session_fork", "session_rename", "session_delete",
    "stash_delete", "model_provider_list", "model_favorite_toggle",
    "session_share", "session_unshare", "session_interrupt", "session_compact",
    "messages_page_up", "messages_page_down", "messages_line_up",
    "messages_line_down", "messages_half_page_up", "messages_half_page_down",
    "messages_first", "messages_last", "messages_next", "messages_previous",
    "messages_last_user", "messages_copy", "messages_undo", "messages_redo",
    "messages_toggle_conceal", "tool_details", "model_list",
    "model_cycle_recent", "model_cycle_recent_reverse",
    "model_cycle_favorite", "model_cycle_favorite_reverse",
    "command_list", "agent_list", "agent_cycle", "agent_cycle_reverse",
    "variant_cycle", "input_clear", "input_paste", "input_submit",
    "input_newline", "input_move_left", "input_move_right",
    "input_move_up", "input_move_down", "input_select_left",
    "input_select_right", "input_select_up", "input_select_down",
    "input_line_home", "input_line_end", "input_select_line_home",
    "input_select_line_end", "input_visual_line_home", "input_visual_line_end",
    "input_select_visual_line_home", "input_select_visual_line_end",
    "input_buffer_home", "input_buffer_end", "input_select_buffer_home",
    "input_select_buffer_end", "input_delete_line", "input_delete_to_line_end",
    "input_delete_to_line_start", "input_backspace", "input_delete",
    "input_undo", "input_redo", "input_word_forward", "input_word_backward",
    "input_select_word_forward", "input_select_word_backward",
    "input_delete_word_forward", "input_delete_word_backward",
    "history_previous", "history_next", "session_child_first",
    "session_child_cycle", "session_child_cycle_reverse", "session_parent",
    "terminal_suspend", "terminal_title_toggle", "tips_toggle",
    "plugin_manager", "display_thinking",
]

# ─── Keybind Defaults (from OpenCode source) ──────────────────────

KEYBIND_DEFAULTS: dict[str, str] = {
    "leader": "ctrl+x",
    "app_exit": "ctrl+c,ctrl+d,<leader>q",
    "editor_open": "<leader>e",
    "theme_list": "<leader>t",
    "sidebar_toggle": "<leader>b",
    "scrollbar_toggle": "none",
    "username_toggle": "none",
    "status_view": "<leader>s",
    "session_export": "<leader>x",
    "session_new": "<leader>n",
    "session_list": "<leader>l",
    "session_timeline": "<leader>g",
    "session_fork": "none",
    "session_rename": "ctrl+r",
    "session_delete": "ctrl+d",
    "stash_delete": "ctrl+d",
    "model_provider_list": "ctrl+a",
    "model_favorite_toggle": "ctrl+f",
    "session_share": "none",
    "session_unshare": "none",
    "session_interrupt": "escape",
    "session_compact": "<leader>c",
    "messages_page_up": "pageup,ctrl+alt+b",
    "messages_page_down": "pagedown,ctrl+alt+f",
    "messages_line_up": "ctrl+alt+y",
    "messages_line_down": "ctrl+alt+e",
    "messages_half_page_up": "ctrl+alt+u",
    "messages_half_page_down": "ctrl+alt+d",
    "messages_first": "ctrl+g,home",
    "messages_last": "ctrl+alt+g,end",
    "messages_next": "none",
    "messages_previous": "none",
    "messages_last_user": "none",
    "messages_copy": "<leader>y",
    "messages_undo": "<leader>u",
    "messages_redo": "<leader>r",
    "messages_toggle_conceal": "<leader>h",
    "tool_details": "none",
    "model_list": "<leader>m",
    "model_cycle_recent": "f2",
    "model_cycle_recent_reverse": "shift+f2",
    "model_cycle_favorite": "none",
    "model_cycle_favorite_reverse": "none",
    "command_list": "ctrl+p",
    "agent_list": "<leader>a",
    "agent_cycle": "tab",
    "agent_cycle_reverse": "shift+tab",
    "variant_cycle": "ctrl+t",
    "input_clear": "ctrl+c",
    "input_paste": "ctrl+v",
    "input_submit": "return",
    "input_newline": "shift+return,ctrl+return,alt+return,ctrl+j",
    "input_move_left": "left,ctrl+b",
    "input_move_right": "right,ctrl+f",
    "input_move_up": "up",
    "input_move_down": "down",
    "input_select_left": "shift+left",
    "input_select_right": "shift+right",
    "input_select_up": "shift+up",
    "input_select_down": "shift+down",
    "input_line_home": "ctrl+a",
    "input_line_end": "ctrl+e",
    "input_select_line_home": "ctrl+shift+a",
    "input_select_line_end": "ctrl+shift+e",
    "input_visual_line_home": "alt+a",
    "input_visual_line_end": "alt+e",
    "input_select_visual_line_home": "alt+shift+a",
    "input_select_visual_line_end": "alt+shift+e",
    "input_buffer_home": "home",
    "input_buffer_end": "end",
    "input_select_buffer_home": "shift+home",
    "input_select_buffer_end": "shift+end",
    "input_delete_line": "ctrl+shift+d",
    "input_delete_to_line_end": "ctrl+k",
    "input_delete_to_line_start": "ctrl+u",
    "input_backspace": "backspace,shift+backspace",
    "input_delete": "ctrl+d,delete,shift+delete",
    "input_undo": "ctrl+-,super+z",
    "input_redo": "ctrl+.,super+shift+z",
    "input_word_forward": "alt+f,alt+right,ctrl+right",
    "input_word_backward": "alt+b,alt+left,ctrl+left",
    "input_select_word_forward": "alt+shift+f,alt+shift+right",
    "input_select_word_backward": "alt+shift+b,alt+shift+left",
    "input_delete_word_forward": "alt+d,alt+delete,ctrl+delete",
    "input_delete_word_backward": "ctrl+w,ctrl+backspace,alt+backspace",
    "history_previous": "up",
    "history_next": "down",
    "session_child_first": "<leader>down",
    "session_child_cycle": "right",
    "session_child_cycle_reverse": "left",
    "session_parent": "up",
    "terminal_suspend": "ctrl+z",
    "terminal_title_toggle": "none",
    "tips_toggle": "<leader>h",
    "plugin_manager": "none",
    "display_thinking": "none",
}

# ─── Well-Known Agent Names ────────────────────────────────────────

WELL_KNOWN_AGENTS: list[str] = [
    "build", "plan", "general", "explore",
    "title", "summary", "compaction",
]

# ─── LSP Entry Fields ──────────────────────────────────────────────

LSP_ENTRY_FIELDS: list[FieldDef] = [
    FieldDef(key="command", field_type=FieldType.STRING_LIST,
             description="LSP server command"),
    FieldDef(key="extensions", field_type=FieldType.STRING_LIST,
             description="File extensions"),
    FieldDef(key="disabled", field_type=FieldType.BOOLEAN,
             description="Disable server"),
    FieldDef(key="env", field_type=FieldType.KEY_VALUE_MAP,
             description="Environment variables"),
    FieldDef(key="initialization", field_type=FieldType.OBJECT,
             description="Init options"),
]

# ─── Experimental Fields ───────────────────────────────────────────

EXPERIMENTAL_FIELDS: list[FieldDef] = [
    FieldDef(key="disable_paste_summary", field_type=FieldType.BOOLEAN,
             description="Disable paste summary", parent="experimental"),
    FieldDef(key="batch_tool", field_type=FieldType.BOOLEAN,
             description="Enable batch tool", parent="experimental"),
    FieldDef(key="openTelemetry", field_type=FieldType.BOOLEAN,
             description="Enable OpenTelemetry", parent="experimental"),
    FieldDef(key="primary_tools", field_type=FieldType.STRING_LIST,
             description="Primary tools list", parent="experimental"),
    FieldDef(key="continue_loop_on_deny", field_type=FieldType.BOOLEAN,
             description="Continue loop on deny", parent="experimental"),
    FieldDef(key="mcp_timeout", field_type=FieldType.INTEGER,
             description="MCP timeout (ms)", parent="experimental"),
]

# ─── Enterprise Fields ─────────────────────────────────────────────

ENTERPRISE_FIELDS: list[FieldDef] = [
    FieldDef(key="url", field_type=FieldType.STRING,
             description="Enterprise URL", parent="enterprise"),
]


def validate_field(field_def: FieldDef, value: Any) -> str | None:
    """Validate a value against a field definition.

    Args:
        field_def: The field definition to validate against.
        value: The value to validate.

    Returns:
        Error message string, or None if valid.
    """
    if value is None or value == "":
        if field_def.required:
            return f"{field_def.key} is required"
        return None

    if field_def.field_type == FieldType.INTEGER:
        try:
            v = int(value)
        except (ValueError, TypeError):
            return f"{field_def.key} must be an integer"
        if field_def.min_value is not None and v < field_def.min_value:
            return f"{field_def.key} must be >= {field_def.min_value}"
        if field_def.max_value is not None and v > field_def.max_value:
            return f"{field_def.key} must be <= {field_def.max_value}"

    elif field_def.field_type == FieldType.NUMBER:
        try:
            v = float(value)
        except (ValueError, TypeError):
            return f"{field_def.key} must be a number"
        if field_def.min_value is not None and v < field_def.min_value:
            return f"{field_def.key} must be >= {field_def.min_value}"

    elif field_def.field_type == FieldType.ENUM:
        if str(value) not in field_def.enum_values:
            return (f"{field_def.key} must be one of: "
                    f"{', '.join(field_def.enum_values)}")

    elif field_def.field_type == FieldType.BOOLEAN:
        if not isinstance(value, bool):
            return f"{field_def.key} must be a boolean"

    elif field_def.field_type == FieldType.STRING_LIST:
        if not isinstance(value, list):
            return f"{field_def.key} must be a list of strings"
        if not all(isinstance(item, str) for item in value):
            return f"{field_def.key} must be a list of strings"

    elif field_def.field_type == FieldType.KEY_VALUE_MAP:
        if not isinstance(value, dict):
            return f"{field_def.key} must be a key/value map"

    elif field_def.field_type == FieldType.STRING:
        if field_def.pattern is not None:
            try:
                if not re.match(field_def.pattern, str(value)):
                    return f"{field_def.key} does not match required pattern"
            except re.error:
                pass

    return None


def get_nested(data: dict, dotted_key: str) -> Any:
    """Get a value from a nested dict using dot notation.

    Args:
        data: The dictionary to search.
        dotted_key: Dot-separated key path (e.g., 'server.port').

    Returns:
        The value at the key path, or None if not found.
    """
    keys = dotted_key.split('.')
    current = data
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return None
        current = current[k]
    return current


def set_nested(data: dict, dotted_key: str, value: Any) -> None:
    """Set a value in a nested dict using dot notation.

    Args:
        data: The dictionary to modify.
        dotted_key: Dot-separated key path.
        value: The value to set.
    """
    keys = dotted_key.split('.')
    current = data
    for k in keys[:-1]:
        if k not in current or not isinstance(current[k], dict):
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value


def remove_nested(data: dict, dotted_key: str) -> None:
    """Remove a key from a nested dict using dot notation.

    Args:
        data: The dictionary to modify.
        dotted_key: Dot-separated key path.
    """
    keys = dotted_key.split('.')
    current = data
    for k in keys[:-1]:
        if not isinstance(current, dict) or k not in current:
            return
        current = current[k]
    if isinstance(current, dict):
        current.pop(keys[-1], None)


def _validate_entry_fields(
    entry_data: dict, field_defs: list[FieldDef], entry_name: str
) -> list[str]:
    """Validate a single dynamic dict entry (agent, provider, command, etc.).

    Args:
        entry_data: The entry dict to validate.
        field_defs: Field definitions for this entry type.
        entry_name: Human-readable name for error messages.

    Returns:
        List of error messages (empty if valid).
    """
    errors = []
    for fd in field_defs:
        raw_val = _get_entry_value(entry_data, fd.key)
        err = validate_field(fd, raw_val)
        if err:
            errors.append(f"[{entry_name}] {err}")
    return errors


def _get_entry_value(entry_data: dict, key: str) -> Any:
    """Get a value from an entry dict using dotted key."""
    parts = key.split('.')
    current = entry_data
    for p in parts:
        if not isinstance(current, dict) or p not in current:
            return None
        current = current[p]
    return current


def validate_config(data: dict) -> list[str]:
    """Validate a full opencode config dict.

    Checks all known sections against their field definitions.
    Returns a list of error messages; empty list means valid.

    Args:
        data: The opencode config dict to validate.

    Returns:
        List of human-readable validation error messages.
    """
    errors: list[str] = []

    for fd in GENERAL_FIELDS:
        val = get_nested(data, fd.full_key)
        err = validate_field(fd, val)
        if err:
            errors.append(err)

    for fd in SERVER_FIELDS:
        val = get_nested(data, fd.full_key)
        err = validate_field(fd, val)
        if err:
            errors.append(err)

    for fd in COMPACTION_FIELDS:
        val = get_nested(data, fd.full_key)
        err = validate_field(fd, val)
        if err:
            errors.append(err)

    providers = data.get("provider", {})
    if isinstance(providers, dict):
        for name, entry in providers.items():
            if isinstance(entry, dict):
                errors.extend(_validate_entry_fields(entry, PROVIDER_ENTRY_FIELDS, f"provider.{name}"))

    agents = data.get("agent", {})
    if isinstance(agents, dict):
        for name, entry in agents.items():
            if isinstance(entry, dict):
                errors.extend(_validate_entry_fields(entry, AGENT_ENTRY_FIELDS, f"agent.{name}"))

    permission = data.get("permission", {})
    if isinstance(permission, dict):
        for tool, val in permission.items():
            if tool not in PERMISSION_TOOLS:
                errors.append(f"permission.{tool}: unknown tool '{tool}'")
            elif tool in PERMISSION_ACTION_ONLY_TOOLS:
                if val not in PERMISSION_VALUES:
                    errors.append(f"permission.{tool}: must be one of {PERMISSION_VALUES}")
            elif tool in PERMISSION_RULE_TOOLS:
                if isinstance(val, str):
                    if val not in PERMISSION_VALUES:
                        errors.append(f"permission.{tool}: must be one of {PERMISSION_VALUES}")
                elif isinstance(val, dict):
                    pass
                else:
                    errors.append(f"permission.{tool}: must be string or object")

    commands = data.get("command", {})
    if isinstance(commands, dict):
        for name, entry in commands.items():
            if isinstance(entry, dict):
                errors.extend(_validate_entry_fields(entry, COMMAND_ENTRY_FIELDS, f"command.{name}"))

    formatters = data.get("formatter", {})
    if isinstance(formatters, dict):
        for name, entry in formatters.items():
            if isinstance(entry, dict):
                errors.extend(_validate_entry_fields(entry, FORMATTER_ENTRY_FIELDS, f"formatter.{name}"))

    mcp = data.get("mcp", {})
    if isinstance(mcp, dict):
        for name, entry in mcp.items():
            if isinstance(entry, dict):
                mcp_type = entry.get("type", "local")
                fields = MCP_LOCAL_FIELDS if mcp_type == "local" else MCP_REMOTE_FIELDS
                errors.extend(_validate_entry_fields(entry, fields, f"mcp.{name}"))

    lsp = data.get("lsp", {})
    if isinstance(lsp, dict):
        for name, entry in lsp.items():
            if isinstance(entry, dict):
                errors.extend(_validate_entry_fields(entry, LSP_ENTRY_FIELDS, f"lsp.{name}"))

    experimental = data.get("experimental", {})
    if isinstance(experimental, dict):
        for fd in EXPERIMENTAL_FIELDS:
            val = experimental.get(fd.key)
            err = validate_field(fd, val)
            if err:
                errors.append(f"experimental.{err}")

    enterprise = data.get("enterprise", {})
    if isinstance(enterprise, dict):
        for fd in ENTERPRISE_FIELDS:
            val = enterprise.get(fd.key)
            err = validate_field(fd, val)
            if err:
                errors.append(f"enterprise.{err}")

    return errors

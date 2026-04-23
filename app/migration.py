"""Configuration schema versioning and migration utilities."""

from enum import Enum
from typing import Any, Callable


class SchemaVersion(Enum):
    V1_2 = "v1.2"
    V1_3 = "v1.3"
    UNKNOWN = "unknown"


def _formatter_command_is_string(config: dict[str, Any]) -> bool:
    formatters = config.get("formatter", {})
    if not isinstance(formatters, dict):
        return False
    for entry in formatters.values():
        if isinstance(entry, dict) and "command" in entry:
            if isinstance(entry["command"], str):
                return True
    return False


def _mcp_command_is_string(config: dict[str, Any]) -> bool:
    mcp = config.get("mcp", {})
    if not isinstance(mcp, dict):
        return False
    for entry in mcp.values():
        if isinstance(entry, dict) and "command" in entry:
            if isinstance(entry["command"], str):
                return True
    return False


def detect_version(config: dict[str, Any]) -> SchemaVersion:
    if _formatter_command_is_string(config) or _mcp_command_is_string(config):
        return SchemaVersion.V1_2
    return SchemaVersion.V1_3


MigrationFn = Callable[[dict[str, Any]], dict[str, Any]]


class MigrationRegistry:
    def __init__(self) -> None:
        self._migrations: dict[tuple[str, str], MigrationFn] = {}

    def register(self, from_ver: SchemaVersion, to_ver: SchemaVersion, fn: MigrationFn) -> None:
        self._migrations[(from_ver.value, to_ver.value)] = fn

    def migrate(self, config: dict[str, Any], from_ver: SchemaVersion, to_ver: SchemaVersion) -> dict[str, Any]:
        result = dict(config)
        if from_ver == to_ver:
            return result

        current = from_ver
        while current != to_ver:
            key = (current.value, to_ver.value)
            if key in self._migrations:
                result = self._migrations[key](result)
                current = to_ver
                break

            next_ver = self._find_next_version(current, to_ver)
            if next_ver is None:
                break
            key = (current.value, next_ver.value)
            if key not in self._migrations:
                break
            result = self._migrations[key](result)
            current = next_ver

        return result

    def _find_next_version(self, current: SchemaVersion, target: SchemaVersion) -> SchemaVersion | None:
        return None


def _string_to_list(value: str) -> list[str]:
    return [value] if value else []


def v1_2_to_v1_3(config: dict[str, Any]) -> dict[str, Any]:
    result = dict(config)

    if "formatter" in result and isinstance(result["formatter"], dict):
        result["formatter"] = {
            name: _migrate_formatter_entry(entry)
            for name, entry in result["formatter"].items()
        }

    if "mcp" in result and isinstance(result["mcp"], dict):
        result["mcp"] = {
            name: _migrate_mcp_entry(entry)
            for name, entry in result["mcp"].items()
        }

    return result


def _migrate_formatter_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        return entry
    result = dict(entry)
    if "command" in result and isinstance(result["command"], str):
        result["command"] = _string_to_list(result["command"])
    return result


def _migrate_mcp_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        return entry
    result = dict(entry)
    if "command" in result and isinstance(result["command"], str):
        result["command"] = _string_to_list(result["command"])
    return result
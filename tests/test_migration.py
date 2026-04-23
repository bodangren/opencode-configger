"""Tests for configuration migration."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from app.migration import (
    MigrationRegistry,
    SchemaVersion,
    detect_version,
    v1_2_to_v1_3,
)


def test_detect_version_v1_3_current_config():
    config = {
        "formatter": {
            "prettier": {
                "command": ["prettier", "--write"],
                "extensions": [".js"],
            }
        },
        "mcp": {
            "example": {
                "type": "local",
                "command": ["npx", "mcp-server-example"],
            }
        },
    }
    assert detect_version(config) == SchemaVersion.V1_3


def test_detect_version_v1_2_formatter_string_command():
    config = {
        "formatter": {
            "prettier": {
                "command": "prettier --write",
                "extensions": [".js"],
            }
        },
    }
    assert detect_version(config) == SchemaVersion.V1_2


def test_detect_version_v1_2_mcp_string_command():
    config = {
        "mcp": {
            "example": {
                "type": "local",
                "command": "npx mcp-server-example",
            }
        },
    }
    assert detect_version(config) == SchemaVersion.V1_2


def test_detect_version_v1_3_no_formatters():
    config = {"model": "anthropic/claude-3-5-sonnet"}
    assert detect_version(config) == SchemaVersion.V1_3


def test_v1_2_to_v1_3_formatter_command():
    config = {
        "formatter": {
            "prettier": {
                "command": "prettier --write",
                "extensions": [".js"],
            }
        }
    }
    result = v1_2_to_v1_3(config)
    assert result["formatter"]["prettier"]["command"] == ["prettier --write"]


def test_v1_2_to_v1_3_formatter_already_list():
    config = {
        "formatter": {
            "prettier": {
                "command": ["prettier", "--write"],
            }
        }
    }
    result = v1_2_to_v1_3(config)
    assert result["formatter"]["prettier"]["command"] == ["prettier", "--write"]


def test_v1_2_to_v1_3_mcp_local_command():
    config = {
        "mcp": {
            "example": {
                "type": "local",
                "command": "npx mcp-server-example",
            }
        }
    }
    result = v1_2_to_v1_3(config)
    assert result["mcp"]["example"]["command"] == ["npx mcp-server-example"]


def test_v1_2_to_v1_3_mcp_already_list():
    config = {
        "mcp": {
            "example": {
                "type": "local",
                "command": ["npx", "mcp-server-example"],
            }
        }
    }
    result = v1_2_to_v1_3(config)
    assert result["mcp"]["example"]["command"] == ["npx", "mcp-server-example"]


def test_v1_2_to_v1_3_preserves_unknown_keys():
    config = {
        "formatter": {"prettier": {"command": "prettier --write"}},
        "unknownTopLevel": {"foo": "bar"},
        "server": {"port": 8080},
    }
    result = v1_2_to_v1_3(config)
    assert "unknownTopLevel" in result
    assert result["server"] == {"port": 8080}


def test_v1_2_to_v1_3_empty_formatter():
    config = {"formatter": {}}
    result = v1_2_to_v1_3(config)
    assert result["formatter"] == {}


def test_v1_2_to_v1_3_no_formatter_no_mcp():
    config = {"model": "anthropic/claude-3-5-sonnet"}
    result = v1_2_to_v1_3(config)
    assert result["model"] == "anthropic/claude-3-5-sonnet"


def test_migration_registry_register_and_migrate():
    registry = MigrationRegistry()
    registry.register(SchemaVersion.V1_2, SchemaVersion.V1_3, v1_2_to_v1_3)

    config = {
        "formatter": {
            "prettier": {
                "command": "prettier --write",
            }
        }
    }
    result = registry.migrate(config, SchemaVersion.V1_2, SchemaVersion.V1_3)
    assert result["formatter"]["prettier"]["command"] == ["prettier --write"]


def test_migration_registry_same_version_returns_unchanged():
    registry = MigrationRegistry()
    config = {"model": "test"}
    result = registry.migrate(config, SchemaVersion.V1_3, SchemaVersion.V1_3)
    assert result == config


def test_migration_registry_preserves_unknown_keys():
    registry = MigrationRegistry()
    registry.register(SchemaVersion.V1_2, SchemaVersion.V1_3, v1_2_to_v1_3)

    config = {
        "formatter": {"prettier": {"command": "prettier"}},
        "unknownKey": {"nested": "value"},
    }
    result = registry.migrate(config, SchemaVersion.V1_2, SchemaVersion.V1_3)
    assert "unknownKey" in result
    assert result["unknownKey"] == {"nested": "value"}


def test_migrate_cli_v1_2_to_v1_3():
    from app.main import _migrate_cli

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test_config.json"
        config = {
            "formatter": {
                "prettier": {"command": "prettier --write", "extensions": [".js"]}
            }
        }
        path.write_text(json.dumps(config))

        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            _migrate_cli(path)
        finally:
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

        assert "Migrating:" in output
        assert "formatter" in output

        migrated = json.loads(path.read_text())
        assert migrated["formatter"]["prettier"]["command"] == ["prettier --write"]

        backup = path.with_suffix(path.suffix + ".bak")
        assert backup.exists()
"""Tests for scanner modules."""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.scanners import (
    McpDescriptor,
    McpScanner,
    PluginDescriptor,
    PluginScanner,
)


class TestPluginScanner:
    @pytest.fixture
    def scanner(self) -> PluginScanner:
        return PluginScanner()

    def test_scan_no_npm(self, scanner: PluginScanner) -> None:
        with patch("shutil.which", return_value=None):
            assert scanner.scan() == []

    def test_scan_timeout(self, scanner: PluginScanner) -> None:
        import subprocess

        with patch("shutil.which", return_value="/usr/bin/npm"):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired("cmd", 3)
                assert scanner.scan() == []

    def test_scan_success(self, scanner: PluginScanner) -> None:
        npm_output = {
            "dependencies": {
                "opencode-plugin-example": {
                    "version": "1.0.0",
                    "description": "An example plugin",
                },
                "regular-package": {"version": "2.0.0"},
            }
        }
        with patch("shutil.which", return_value="/usr/bin/npm"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout=json.dumps(npm_output), stderr=""
                )
                plugins = scanner.scan()
                assert len(plugins) == 1
                assert plugins[0].name == "opencode-plugin-example"
                assert plugins[0].version == "1.0.0"

    def test_scan_detects_by_keyword(self, scanner: PluginScanner) -> None:
        npm_output = {
            "dependencies": {
                "my-opencode-adapter": {
                    "version": "0.5.0",
                    "keywords": ["opencode-plugin", "some-other-tag"],
                },
            }
        }
        with patch("shutil.which", return_value="/usr/bin/npm"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout=json.dumps(npm_output), stderr=""
                )
                plugins = scanner.scan()
                assert len(plugins) == 1
                assert plugins[0].name == "my-opencode-adapter"

    def test_scan_non_zero_exit(self, scanner: PluginScanner) -> None:
        with patch("shutil.which", return_value="/usr/bin/npm"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1, stdout="", stderr="npm error"
                )
                assert scanner.scan() == []

    def test_scan_invalid_json(self, scanner: PluginScanner) -> None:
        with patch("shutil.which", return_value="/usr/bin/npm"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout="not json", stderr=""
                )
                assert scanner.scan() == []


class TestMcpScanner:
    @pytest.fixture
    def scanner(self) -> McpScanner:
        return McpScanner()

    def test_scan_no_mcp_section(self, scanner: McpScanner) -> None:
        assert scanner.scan({}) == []

    def test_scan_skips_non_stdio(self, scanner: McpScanner) -> None:
        config = {
            "mcp": {
                "sse-server": {
                    "type": "sse",
                    "url": "https://example.com",
                }
            }
        }
        assert scanner.scan(config) == []

    def test_scan_stdio_timeout(self, scanner: McpScanner) -> None:
        import subprocess

        config = {
            "mcp": {
                "my-server": {
                    "type": "stdio",
                    "command": "my-mcp-server",
                    "args": [],
                }
            }
        }
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 3)
            desc = scanner.scan(config)
            assert len(desc) == 1
            assert desc[0].server_name == "my-server"
            assert desc[0].config_keys == []

    def test_scan_stdio_parses_help_output(self, scanner: McpScanner) -> None:
        config = {
            "mcp": {
                "example-mcp": {
                    "type": "stdio",
                    "command": "example-mcp-server",
                    "args": ["--flag"],
                }
            }
        }
        help_output = (
            "example-mcp-server v1.0\n"
            "Usage: example-mcp-server [OPTIONS]\n"
            "  --config-api-key KEY    Set the API key\n"
            "  --config-timeout SECS   Set timeout\n"
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=help_output, stderr=""
            )
            desc = scanner.scan(config)
            assert len(desc) == 1
            assert desc[0].server_name == "example-mcp"
            assert "api-key" in desc[0].config_keys
            assert "timeout" in desc[0].config_keys

    def test_scan_multiple_servers(self, scanner: McpScanner) -> None:
        config = {
            "mcp": {
                "server-a": {
                    "type": "stdio",
                    "command": "server-a",
                    "args": [],
                },
                "server-b": {
                    "type": "stdio",
                    "command": "server-b",
                    "args": [],
                },
            }
        }
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="--config-key value\n", stderr=""
            )
            desc = scanner.scan(config)
            assert len(desc) == 2
            names = {d.server_name for d in desc}
            assert names == {"server-a", "server-b"}

    def test_parse_config_flags_duplicates(self, scanner: McpScanner) -> None:
        output = "--config-key val\n--config-key val\n"
        keys = scanner._parse_config_flags(output)
        assert keys.count("key") == 1

    def test_scan_invalid_server_config(self, scanner: McpScanner) -> None:
        config = {"mcp": {"bad": "not-a-dict"}}
        assert scanner.scan(config) == []

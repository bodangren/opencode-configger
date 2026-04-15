"""Scanner for discovering MCP server configuration keys."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class McpDescriptor:
    """Describes a discovered MCP server and its config keys."""

    server_name: str
    config_keys: list[str] = field(default_factory=list)
    command: str | None = None


class McpScanner:
    """Scans configured MCP servers for their config key requirements."""

    TIMEOUT_SECONDS = 3
    CONFIG_FLAG_PATTERN = re.compile(r"--config-(\w[\w-]*)")

    def scan(self, config: dict[str, Any]) -> list[McpDescriptor]:
        """Scan MCP servers defined in the config for their config keys.

        Args:
            config: The full OpenCode config dict containing an 'mcp' key.

        Returns:
            List of McpDescriptor objects for stdio-based MCP servers.
        """
        mcp_entries = config.get("mcp", {})
        if not mcp_entries:
            return []

        descriptors: list[McpDescriptor] = []
        for server_name, server_config in mcp_entries.items():
            if not isinstance(server_config, dict):
                continue
            if server_config.get("type") == "stdio":
                desc = self._scan_stdio_server(
                    server_name, server_config
                )
                descriptors.append(desc)

        return descriptors

    def _scan_stdio_server(
        self, server_name: str, server_config: dict[str, Any]
    ) -> McpDescriptor:
        """Run --help on a stdio MCP server and parse config keys."""
        command = server_config.get("command")
        if not command:
            return McpDescriptor(server_name=server_name)

        args = server_config.get("args", [])
        full_cmd = [command] + args + ["--help"]

        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "MCP server '%s' --help timed out after %ds",
                server_name,
                self.TIMEOUT_SECONDS,
            )
            return McpDescriptor(server_name=server_name, command=command)
        except Exception as e:
            logger.warning(
                "MCP server '%s' --help failed: %s", server_name, e
            )
            return McpDescriptor(server_name=server_name, command=command)

        config_keys = self._parse_config_flags(result.stdout + result.stderr)
        return McpDescriptor(
            server_name=server_name,
            command=command,
            config_keys=config_keys,
        )

    def _parse_config_flags(self, output: str) -> list[str]:
        """Extract --config-* flag names from help output."""
        keys: list[str] = []
        for match in self.CONFIG_FLAG_PATTERN.finditer(output):
            keys.append(match.group(1))
        return list(dict.fromkeys(keys))


def scan_mcp_servers(config: dict[str, Any]) -> list[McpDescriptor]:
    """Convenience function that creates an McpScanner and runs scan."""
    return McpScanner().scan(config)
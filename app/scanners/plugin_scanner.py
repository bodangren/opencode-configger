"""Scanner for discovering locally installed OpenCode plugins."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PluginDescriptor:
    """Describes a discovered plugin and its config keys."""

    name: str
    config_keys: list[str] = field(default_factory=list)
    version: str | None = None
    description: str | None = None


class PluginScanner:
    """Scans the local npm environment for installed OpenCode plugins."""

    PLUGIN_PREFIX = "opencode-plugin-"
    TIMEOUT_SECONDS = 3

    def scan(self) -> list[PluginDescriptor]:
        """Run npm ls to discover installed plugins.

        Returns:
            List of PluginDescriptor objects for discovered plugins.
        """
        npm_ls = shutil.which("npm")
        if not npm_ls:
            logger.warning("npm not found; cannot scan for plugins")
            return []

        try:
            result = subprocess.run(
                [npm_ls, "ls", "--json", "--depth=0"],
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            logger.warning("npm ls timed out after %ds", self.TIMEOUT_SECONDS)
            return []
        except Exception as e:
            logger.warning("npm ls failed: %s", e)
            return []

        if result.returncode != 0:
            logger.warning("npm ls returned non-zero: %s", result.stderr)
            return []

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.warning("npm ls output was not valid JSON")
            return []

        return self._parse_npm_ls(data)

    def _parse_npm_ls(self, data: dict[str, Any]) -> list[PluginDescriptor]:
        """Parse npm ls JSON output into PluginDescriptor list."""
        plugins: list[PluginDescriptor] = []
        dependencies: dict[str, Any] = data.get("dependencies", {})

        for name, info in dependencies.items():
            if self._is_opencode_plugin(name, info):
                plugins.append(
                    PluginDescriptor(
                        name=name,
                        version=info.get("version"),
                        description=info.get("description"),
                        config_keys=self._extract_config_keys(info),
                    )
                )

        return plugins

    def _is_opencode_plugin(self, name: str, info: dict[str, Any]) -> bool:
        """Check if a package is an OpenCode plugin."""
        if name.startswith(self.PLUGIN_PREFIX):
            return True
        keywords = info.get("keywords", [])
        if isinstance(keywords, list) and "opencode-plugin" in keywords:
            return True
        return False

    def _extract_config_keys(self, info: dict[str, Any]) -> list[str]:
        """Extract configuration keys from plugin metadata."""
        return []


def scan_plugins() -> list[PluginDescriptor]:
    """Convenience function that creates a PluginScanner and runs scan."""
    return PluginScanner().scan()
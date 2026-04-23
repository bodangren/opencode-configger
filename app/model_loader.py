"""Model loading backend for OpenCode model discovery."""

import subprocess
import threading
from dataclasses import dataclass
from typing import Callable


class ModelLoadError(Exception):
    """Raised when model loading fails."""
    pass


@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
    context_window: int | None = None


ModelMap = dict[str, list[str]]


def _run_opencode_models_command(timeout: int = 10) -> str:
    commands = [
        ["opencode", "models", "--json"],
        ["opencode-cli", "models", "--json"],
        ["opencode", "models"],
        ["opencode-cli", "models"],
    ]

    last_error: Exception | None = None
    for command in commands:
        try:
            proc = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except Exception as exc:
            last_error = exc
            continue

        stdout = proc.stdout.strip()
        if stdout:
            return stdout

    if last_error is not None:
        if isinstance(last_error, FileNotFoundError):
            raise ModelLoadError("opencode not found on PATH")
        if isinstance(last_error, subprocess.TimeoutExpired):
            raise ModelLoadError("Model fetch timed out")
        raise ModelLoadError(f"Model fetch failed: {last_error}")
    raise ModelLoadError("No output from opencode models CLI")


class ModelLoader:
    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def load_sync(self) -> ModelMap:
        raw = _run_opencode_models_command(self.timeout)
        return _parse_models_output(raw)

    def load_async(
        self,
        on_done: Callable[[ModelMap], None] | None = None,
        error_callback: Callable[[ModelLoadError], None] | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self._stop_event.clear()
        timeout = timeout_seconds if timeout_seconds is not None else self.timeout
        self._thread = threading.Thread(
            target=self._async_worker,
            args=(on_done, error_callback, timeout),
            daemon=True,
        )
        self._thread.start()

    def _async_worker(
        self,
        on_done: Callable[[ModelMap], None] | None,
        error_callback: Callable[[ModelLoadError], None] | None,
        timeout: int,
    ) -> None:
        try:
            result = self.load_sync()
            if on_done is not None:
                on_done(result)
        except ModelLoadError as exc:
            if error_callback is not None:
                error_callback(exc)

    def join(self, timeout: float | None = None) -> None:
        if self._thread is not None:
            self._thread.join(timeout)


def _parse_models_output(raw: str) -> ModelMap:
    import json
    import re

    grouped: ModelMap = {}

    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            if all(isinstance(v, list) for v in data.values()):
                for provider, models in data.items():
                    grouped[str(provider)] = [str(m) for m in models]
                return grouped

            models_list = data.get("models")
            if isinstance(models_list, list):
                for entry in models_list:
                    if not isinstance(entry, dict):
                        continue
                    model_name = str(entry.get("id") or entry.get("name") or "")
                    if not model_name:
                        continue
                    provider = model_name.split("/", 1)[0]
                    grouped.setdefault(provider, []).append(model_name)
                return grouped

        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, str):
                    model_name = entry
                elif isinstance(entry, dict):
                    model_name = str(entry.get("id") or entry.get("name") or "")
                else:
                    continue
                if not model_name:
                    continue
                provider = model_name.split("/", 1)[0]
                grouped.setdefault(provider, []).append(model_name)
            return grouped

    except json.JSONDecodeError:
        pass

    for line in raw.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        match = re.search(r"([a-zA-Z0-9._-]+/[a-zA-Z0-9._:-]+)", cleaned)
        if not match:
            continue
        model_name = match.group(1)
        provider = model_name.split("/", 1)[0]
        grouped.setdefault(provider, []).append(model_name)

    if not grouped:
        raise ModelLoadError("No output from opencode models CLI")

    return grouped
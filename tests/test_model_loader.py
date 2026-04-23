"""Tests for ModelLoader."""

import json
import subprocess
import threading
from unittest.mock import MagicMock, patch

import pytest

from app.model_loader import ModelInfo, ModelLoader, ModelLoadError


@pytest.fixture
def mock_successful_json_output():
    return json.dumps({
        "openai": ["gpt-4.1", "gpt-4.1-mini"],
        "anthropic": ["claude-3.7-sonnet"],
    })


@pytest.fixture
def mock_successful_text_output():
    return """Available models:
    - openai/gpt-4.1
    - openai/gpt-4.1-mini
    - anthropic/claude-3.7-sonnet"""


@pytest.fixture
def mock_list_json_output():
    return json.dumps(["openai/gpt-4.1", "anthropic/claude-3.7-sonnet"])


class TestModelInfo:
    def test_model_info_creation(self) -> None:
        info = ModelInfo(id="openai/gpt-4.1", name="GPT-4.1", provider="openai", context_window=128000)
        assert info.id == "openai/gpt-4.1"
        assert info.name == "GPT-4.1"
        assert info.provider == "openai"
        assert info.context_window == 128000

    def test_model_info_optional_context_window(self) -> None:
        info = ModelInfo(id="openai/gpt-4.1", name="GPT-4.1", provider="openai")
        assert info.context_window is None


class TestModelLoaderSuccess:
    def test_load_json_output(self, mock_successful_json_output: str) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_successful_json_output,
                stderr="",
            )
            loader = ModelLoader()
            result = loader.load_sync()
            assert "openai" in result
            assert "anthropic" in result

    def test_load_text_output_falls_back_when_json_fails(self, mock_successful_text_output: str) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_successful_text_output,
                stderr="",
            )
            loader = ModelLoader()
            result = loader.load_sync()
            assert "openai" in result
            assert "anthropic" in result

    def test_load_list_json_format(self, mock_list_json_output: str) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_list_json_output,
                stderr="",
            )
            loader = ModelLoader()
            result = loader.load_sync()
            assert "openai" in result
            assert "anthropic" in result


class TestModelLoaderError:
    def test_opencode_not_on_path(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            loader = ModelLoader()
            with pytest.raises(ModelLoadError) as exc_info:
                loader.load_sync()
            assert "not found" in str(exc_info.value).lower()

    def test_timeout(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("opencode models", 10)
            loader = ModelLoader()
            with pytest.raises(ModelLoadError) as exc_info:
                loader.load_sync()
            assert "timed out" in str(exc_info.value).lower()

    def test_empty_output(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="",
                stderr="",
            )
            loader = ModelLoader()
            with pytest.raises(ModelLoadError) as exc_info:
                loader.load_sync()
            assert "no output" in str(exc_info.value).lower()


class TestModelLoaderAsync:
    def test_load_async_calls_callback_on_success(self, mock_successful_json_output: str) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_successful_json_output,
                stderr="",
            )
            loader = ModelLoader()
            results: list[dict[str, list[str]]] = []

            def on_done(result: dict[str, list[str]]) -> None:
                results.append(result)

            loader.load_async(on_done)
            loader.join()
            assert len(results) == 1
            assert "openai" in results[0]

    def test_load_async_calls_error_callback(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            loader = ModelLoader()
            errors: list[ModelLoadError] = []

            def on_error(error: ModelLoadError) -> None:
                errors.append(error)

            loader.load_async(error_callback=on_error)
            loader.join()
            assert len(errors) == 1

    def test_load_async_timeout(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("opencode models", 10)
            loader = ModelLoader()
            errors: list[ModelLoadError] = []

            def on_error(error: ModelLoadError) -> None:
                errors.append(error)

            loader.load_async(error_callback=on_error, timeout_seconds=1)
            loader.join()
            assert len(errors) == 1
            assert "timed out" in str(errors[0]).lower()

    def test_join_does_not_block_if_not_started(self) -> None:
        loader = ModelLoader()
        loader.join()
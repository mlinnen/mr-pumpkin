"""
Test suite for skill/list_models.py — Model Listing Skill

Tests the ModelListProvider ABC, GeminiModelProvider, OpenAIModelProvider,
get_provider() factory, and the CLI entry point using mocked SDK clients.

Author: Mylo (Tester)
"""

import os
import sys
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from skill.list_models import (
        GeminiModelProvider,
        OpenAIModelProvider,
        get_provider,
        list_provider_names,
        main,
    )
    SKILL_AVAILABLE = True
except ImportError:
    SKILL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not SKILL_AVAILABLE,
    reason="skill/list_models.py not available"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_gemini_model(name: str):
    m = MagicMock()
    m.name = name
    return m


def _make_openai_model(model_id: str):
    m = MagicMock()
    m.id = model_id
    return m


# ---------------------------------------------------------------------------
# GeminiModelProvider
# ---------------------------------------------------------------------------

class TestGeminiModelProvider:
    def _provider(self, model_names):
        """Return a GeminiModelProvider with a mocked client."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch("skill.list_models.GeminiModelProvider.__init__", lambda self, **kw: None):
                provider = GeminiModelProvider.__new__(GeminiModelProvider)
                client = MagicMock()
                client.models.list.return_value = [_make_gemini_model(n) for n in model_names]
                provider._client = client
                return provider

    def test_list_models_returns_sorted(self):
        provider = self._provider(["models/gemini-pro", "models/gemini-flash", "models/gemini-ultra"])
        result = provider.list_models()
        assert result == sorted(result)

    def test_list_models_no_filter(self):
        names = ["models/gemini-pro", "models/gemini-flash"]
        provider = self._provider(names)
        result = provider.list_models()
        assert set(result) == set(names)

    def test_list_models_filter_matches(self):
        provider = self._provider(["models/gemini-flash", "models/gemini-pro", "models/text-bison"])
        result = provider.list_models(filter="flash")
        assert result == ["models/gemini-flash"]

    def test_list_models_filter_case_insensitive(self):
        provider = self._provider(["models/Gemini-Flash-1.5", "models/gemini-pro"])
        result = provider.list_models(filter="FLASH")
        assert result == ["models/Gemini-Flash-1.5"]

    def test_list_models_filter_no_match(self):
        provider = self._provider(["models/gemini-pro"])
        result = provider.list_models(filter="gpt")
        assert result == []

    def test_provider_name(self):
        provider = self._provider([])
        assert provider.provider_name == "Gemini"

    def test_missing_api_key_raises(self):
        env = {k: v for k, v in os.environ.items() if k not in ("GEMINI_API_KEY", "GOOGLE_API_KEY")}
        with patch.dict(os.environ, env, clear=True):
            with patch("skill.list_models.GeminiModelProvider.__init__", GeminiModelProvider.__init__):
                with patch("google.genai.Client"):
                    with pytest.raises(EnvironmentError, match="GEMINI_API_KEY"):
                        GeminiModelProvider()

    def test_missing_sdk_raises_import_error(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "key"}):
            with patch.dict(sys.modules, {"google": None, "google.genai": None}):
                with pytest.raises(ImportError, match="google-genai"):
                    GeminiModelProvider()


# ---------------------------------------------------------------------------
# OpenAIModelProvider
# ---------------------------------------------------------------------------

class TestOpenAIModelProvider:
    def _provider(self, model_ids):
        """Return an OpenAIModelProvider with a mocked client."""
        provider = OpenAIModelProvider.__new__(OpenAIModelProvider)
        client = MagicMock()
        client.models.list.return_value = MagicMock(data=[_make_openai_model(i) for i in model_ids])
        provider._client = client
        return provider

    def test_list_models_returns_sorted(self):
        provider = self._provider(["gpt-4o", "gpt-3.5-turbo", "gpt-4"])
        result = provider.list_models()
        assert result == sorted(result)

    def test_list_models_no_filter(self):
        ids = ["gpt-4o", "gpt-3.5-turbo"]
        provider = self._provider(ids)
        result = provider.list_models()
        assert set(result) == set(ids)

    def test_list_models_filter(self):
        provider = self._provider(["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
        result = provider.list_models(filter="gpt-4")
        assert "gpt-3.5-turbo" not in result
        assert "gpt-4o" in result
        assert "gpt-4" in result

    def test_list_models_filter_case_insensitive(self):
        provider = self._provider(["GPT-4O", "gpt-3.5"])
        result = provider.list_models(filter="gpt-4o")
        assert result == ["GPT-4O"]

    def test_list_models_filter_no_match(self):
        provider = self._provider(["gpt-4o"])
        result = provider.list_models(filter="claude")
        assert result == []

    def test_provider_name(self):
        provider = self._provider([])
        assert provider.provider_name == "OpenAI"

    def test_missing_api_key_raises(self):
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            with patch("skill.list_models.OpenAIModelProvider.__init__", OpenAIModelProvider.__init__):
                with patch("openai.OpenAI"):
                    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
                        OpenAIModelProvider()

    def test_missing_sdk_raises_import_error(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "key"}):
            with patch.dict(sys.modules, {"openai": None}):
                with pytest.raises(ImportError, match="openai"):
                    OpenAIModelProvider()


# ---------------------------------------------------------------------------
# get_provider factory
# ---------------------------------------------------------------------------

class TestGetProvider:
    def test_returns_gemini_provider(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "key"}):
            with patch("skill.list_models.GeminiModelProvider.__init__", lambda self, **kw: None):
                p = get_provider("gemini")
                assert isinstance(p, GeminiModelProvider)

    def test_returns_openai_provider(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "key"}):
            with patch("skill.list_models.OpenAIModelProvider.__init__", lambda self, **kw: None):
                p = get_provider("openai")
                assert isinstance(p, OpenAIModelProvider)

    def test_case_insensitive(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "key"}):
            with patch("skill.list_models.GeminiModelProvider.__init__", lambda self, **kw: None):
                p = get_provider("GEMINI")
                assert isinstance(p, GeminiModelProvider)

    def test_unknown_provider_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("anthropic")

    def test_unknown_provider_lists_supported(self):
        with pytest.raises(ValueError, match="gemini"):
            get_provider("unknown")


# ---------------------------------------------------------------------------
# list_provider_names
# ---------------------------------------------------------------------------

def test_list_provider_names_returns_sorted():
    names = list_provider_names()
    assert names == sorted(names)

def test_list_provider_names_contains_expected():
    names = list_provider_names()
    assert "gemini" in names
    assert "openai" in names


# ---------------------------------------------------------------------------
# CLI — main()
# ---------------------------------------------------------------------------

class TestCLI:
    def _mock_provider(self, model_ids, provider_name="Gemini"):
        provider = MagicMock()
        provider.provider_name = provider_name
        provider.list_models.return_value = sorted(model_ids)
        return provider

    def test_list_single_provider(self, capsys):
        with patch("skill.list_models.get_provider", return_value=self._mock_provider(["gemini-flash", "gemini-pro"])):
            code = main(["--provider", "gemini"])
        assert code == 0
        out = capsys.readouterr().out
        assert "gemini-flash" in out
        assert "gemini-pro" in out

    def test_filter_passed_to_provider(self, capsys):
        provider = self._mock_provider(["gemini-flash"])
        with patch("skill.list_models.get_provider", return_value=provider):
            code = main(["--provider", "gemini", "--filter", "flash"])
        assert code == 0
        provider.list_models.assert_called_once_with(filter="flash")

    def test_no_models_matched(self, capsys):
        with patch("skill.list_models.get_provider", return_value=self._mock_provider([])):
            code = main(["--provider", "gemini", "--filter", "zzz"])
        assert code == 0
        out = capsys.readouterr().out
        assert "No models matched" in out

    def test_unknown_provider_exits_2(self, capsys):
        code = main(["--provider", "fakeprovider"])
        assert code == 2

    def test_api_error_exits_1(self, capsys):
        provider = MagicMock()
        provider.list_models.side_effect = Exception("network timeout")
        with patch("skill.list_models.get_provider", return_value=provider):
            code = main(["--provider", "gemini"])
        assert code == 1

    def test_all_providers_flag(self, capsys):
        providers = {
            "gemini": self._mock_provider(["gemini-flash"], "Gemini"),
            "openai": self._mock_provider(["gpt-4o"], "OpenAI"),
        }
        with patch("skill.list_models.get_provider", side_effect=lambda name, **kw: providers[name]):
            code = main(["--all"])
        assert code == 0
        out = capsys.readouterr().out
        assert "gemini-flash" in out
        assert "gpt-4o" in out

    def test_all_providers_partial_error_exits_1(self, capsys):
        def _side_effect(name, **kw):
            if name == "gemini":
                raise EnvironmentError("no key")
            return self._mock_provider(["gpt-4o"], "OpenAI")

        with patch("skill.list_models.get_provider", side_effect=_side_effect):
            code = main(["--all"])
        assert code == 1

    def test_env_error_exits_1(self, capsys):
        with patch("skill.list_models.get_provider", side_effect=EnvironmentError("no key")):
            code = main(["--provider", "gemini"])
        assert code == 1

    def test_model_count_in_output(self, capsys):
        models = ["gemini-flash", "gemini-pro", "gemini-ultra"]
        with patch("skill.list_models.get_provider", return_value=self._mock_provider(models)):
            main(["--provider", "gemini"])
        out = capsys.readouterr().out
        assert "3" in out

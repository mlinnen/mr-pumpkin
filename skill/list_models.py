"""
Mr. Pumpkin — List available AI models by provider.

Queries the live API for each provider and returns a sorted list of model IDs.
Supports pluggable providers; use ``get_provider()`` as the factory.

Usage:
    from skill.list_models import get_provider
    provider = get_provider("gemini")
    models = provider.list_models()

    # or filter by name fragment
    models = provider.list_models(filter="flash")

CLI:
    python -m skill.list_models
    python -m skill.list_models --provider openai
    python -m skill.list_models --provider gemini --filter flash
    python -m skill.list_models --all

Exit codes:
    0 — success
    1 — API or network error
    2 — argument error
"""

import argparse
import os
import sys
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class ModelListProvider(ABC):
    """Abstract base class for model-listing backends."""

    @abstractmethod
    def list_models(self, filter: str = "") -> list[str]:
        """Return a sorted list of model IDs available from this provider.

        Args:
            filter: Optional substring to filter model IDs (case-insensitive).

        Returns:
            Sorted list of matching model ID strings.
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name (e.g. "Gemini", "OpenAI")."""


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

class GeminiModelProvider(ModelListProvider):
    """Lists models available from the Google Gemini API.

    API key is read from the ``GEMINI_API_KEY`` environment variable,
    falling back to ``GOOGLE_API_KEY``.

    Raises:
        EnvironmentError: If no API key is found in the environment.
        ImportError: If the ``google-genai`` package is not installed.
    """

    def __init__(self, api_key: str = None):
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError(
                "google-genai is required for GeminiModelProvider. "
                "Install it with: pip install google-genai"
            ) from exc

        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            raise EnvironmentError(
                "No Gemini API key found. Set the GEMINI_API_KEY environment variable."
            )

        self._client = genai.Client(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Gemini"

    def list_models(self, filter: str = "") -> list[str]:
        """Return sorted Gemini model IDs, optionally filtered by substring.

        Args:
            filter: Case-insensitive substring to match against model IDs.

        Returns:
            Sorted list of matching model ID strings.
        """
        models = self._client.models.list()
        ids = [m.name for m in models]
        if filter:
            ids = [m for m in ids if filter.lower() in m.lower()]
        return sorted(ids)


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------

class OpenAIModelProvider(ModelListProvider):
    """Lists models available from the OpenAI API.

    API key is read from the ``OPENAI_API_KEY`` environment variable.

    Raises:
        EnvironmentError: If no API key is found in the environment.
        ImportError: If the ``openai`` package is not installed.
    """

    def __init__(self, api_key: str = None, base_url: str = "https://api.openai.com/v1"):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai is required for OpenAIModelProvider. "
                "Install it with: pip install openai"
            ) from exc

        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise EnvironmentError(
                "No OpenAI API key found. Set the OPENAI_API_KEY environment variable."
            )

        self._client = OpenAI(api_key=api_key, base_url=base_url)

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def list_models(self, filter: str = "") -> list[str]:
        """Return sorted OpenAI model IDs, optionally filtered by substring.

        Args:
            filter: Case-insensitive substring to match against model IDs.

        Returns:
            Sorted list of matching model ID strings.
        """
        response = self._client.models.list()
        ids = [m.id for m in response.data]
        if filter:
            ids = [m for m in ids if filter.lower() in m.lower()]
        return sorted(ids)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_PROVIDERS = {
    "gemini": GeminiModelProvider,
    "openai": OpenAIModelProvider,
}


def get_provider(name: str, **kwargs) -> ModelListProvider:
    """Instantiate a ModelListProvider by name.

    Args:
        name: Provider name — ``"gemini"`` or ``"openai"`` (case-insensitive).
        **kwargs: Passed through to the provider constructor (e.g., ``api_key``).

    Returns:
        A ready-to-use ModelListProvider instance.

    Raises:
        ValueError: If ``name`` is not a known provider.
        EnvironmentError: If the required API key is missing.
        ImportError: If the provider's SDK package is not installed.
    """
    key = name.lower()
    cls = _PROVIDERS.get(key)
    if cls is None:
        supported = ", ".join(sorted(_PROVIDERS))
        raise ValueError(
            f"Unknown provider: {name!r}. Supported providers: {supported}"
        )
    return cls(**kwargs)


def list_provider_names() -> list[str]:
    """Return the names of all supported providers."""
    return sorted(_PROVIDERS)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mr-pumpkin-list-models",
        description="List AI models available from a provider.",
    )
    p.add_argument(
        "--provider", "-p",
        default="gemini",
        help="Provider to query: gemini or openai (default: gemini).",
    )
    p.add_argument(
        "--filter", "-f",
        default="",
        help="Optional substring to filter model IDs (case-insensitive).",
    )
    p.add_argument(
        "--all", "-a",
        action="store_true",
        dest="all_providers",
        help="Query all supported providers and print results grouped by provider.",
    )
    p.add_argument(
        "--api-key",
        help="Override API key for the selected provider (reads from env var if not specified).",
    )
    return p


def main(argv=None) -> int:
    """Main entry point for the list-models CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    provider_kwargs = {}
    if args.api_key:
        provider_kwargs["api_key"] = args.api_key

    if args.all_providers:
        any_error = False
        for name in list_provider_names():
            print(f"\n── {name.upper()} ──")
            try:
                provider = get_provider(name, **provider_kwargs)
                models = provider.list_models(filter=args.filter)
                if models:
                    for m in models:
                        print(f"  {m}")
                else:
                    print("  (no models matched)")
            except (EnvironmentError, ImportError) as exc:
                print(f"  ERROR: {exc}", file=sys.stderr)
                any_error = True
            except Exception as exc:
                print(f"  ERROR: {exc}", file=sys.stderr)
                any_error = True
        return 1 if any_error else 0

    try:
        provider = get_provider(args.provider, **provider_kwargs)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (EnvironmentError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        models = provider.list_models(filter=args.filter)
    except Exception as exc:
        print(f"ERROR: Failed to list models — {exc}", file=sys.stderr)
        return 1

    if models:
        print(f"{provider.provider_name} models ({len(models)}):")
        for m in models:
            print(f"  {m}")
    else:
        print(f"No models matched for provider '{args.provider}'.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

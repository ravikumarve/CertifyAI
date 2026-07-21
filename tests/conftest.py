"""pytest configuration and shared fixtures.

Automatically loads environment variables from the project root .env file
so integration tests can access API keys.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from _pytest.config.argparsing import Parser

# ---------------------------------------------------------------------------
# Auto-load .env at import time (runs before any test collection)
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(_env_path, override=False)
    except ImportError:
        pass  # python-dotnet not installed — env vars must be set manually


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require API keys.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires API keys).",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-integration"):
        return  # run all tests
    skip_integration = pytest.mark.skip(reason="Need --run-integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)

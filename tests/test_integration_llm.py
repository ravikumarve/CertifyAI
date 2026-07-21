"""Integration tests for LiteLLM with real provider.

These tests require a valid API key and are skipped by default.
Run with: pytest --run-integration

Note: NVIDIA NIM free tier has aggressive rate limits. Tests
are designed to handle 429 responses gracefully.
"""

from __future__ import annotations

import os

import pytest

from certifyai.engine.lite_llm import LLMClient, LLMError
from certifyai.engine.models import AttackCategory, ProviderConfig
from certifyai.engine.registry import PluginRegistry
from certifyai.engine.runner import AttackRunner, RunConfig

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _provider_config() -> ProviderConfig:
    """Build a ProviderConfig from environment variables."""
    return ProviderConfig(
        provider=os.getenv("CERTIFYAI_PROVIDER", "nvidia_nim"),
        model=os.getenv("CERTIFYAI_MODEL", "meta/llama-3.1-8b-instruct"),
        api_key=os.getenv("CERTIFYAI_API_KEY"),
        endpoint=os.getenv("CERTIFYAI_ENDPOINT") or None,
        max_retries=1,
        timeout_seconds=60,
    )


def _skip_if_no_key() -> None:
    """Skip the test if no API key is available."""
    if not os.getenv("CERTIFYAI_API_KEY"):
        pytest.skip("CERTIFYAI_API_KEY not set — add to .env file")


def _handle_rate_limit(e: Exception) -> None:
    """Pytest-skip on rate limit errors (free tier limitation)."""
    if "429" in str(e) or "RateLimit" in type(e).__name__:
        pytest.skip(f"Rate limited (free tier): {e}")


# ---------------------------------------------------------------------------
# Basic LLM communication tests
# ---------------------------------------------------------------------------


class TestLLMBasicCommunication:
    """Verify we can talk to the LLM provider at all."""

    @pytest.mark.asyncio
    async def test_simple_completion(self) -> None:
        _skip_if_no_key()
        config = _provider_config()
        client = LLMClient(config)

        try:
            response = await client.complete("Say exactly: hello world")
            assert isinstance(response, str)
            assert len(response) > 0
            assert "hello" in response.lower() or "world" in response.lower()
        except LLMError as e:
            _handle_rate_limit(e)
            raise

    @pytest.mark.asyncio
    async def test_empty_prompt(self) -> None:
        _skip_if_no_key()
        config = _provider_config()
        client = LLMClient(config)

        try:
            response = await client.complete("")
            assert isinstance(response, str)
        except LLMError as e:
            _handle_rate_limit(e)
            raise

    @pytest.mark.asyncio
    async def test_long_prompt(self) -> None:
        _skip_if_no_key()
        config = _provider_config()
        client = LLMClient(config)

        try:
            long_prompt = "Write a haiku about artificial intelligence. " * 10
            response = await client.complete(long_prompt, max_tokens=200)
            assert isinstance(response, str)
            assert len(response) > 0
        except LLMError as e:
            _handle_rate_limit(e)
            raise


# ---------------------------------------------------------------------------
# Targeted attack execution test
# ---------------------------------------------------------------------------


class TestAttackExecution:
    """Run a targeted subset of attack scenarios against the LLM.

    We only run one category (prompt_injection) to stay within free-tier
    rate limits while still verifying the end-to-end pipeline.
    """

    @pytest.mark.asyncio
    async def test_single_category_attack(self) -> None:
        _skip_if_no_key()
        provider = _provider_config()
        config = RunConfig(
            provider=provider,
            attack_categories=[AttackCategory.PROMPT_INJECTION],
            concurrency=2,  # low concurrency to avoid rate limits
            dry_run=False,
        )
        registry = PluginRegistry()
        runner = AttackRunner(config, registry=registry)
        summary, results = await runner.run_all()

        assert summary.total_attacks == len(results)
        assert summary.total_attacks > 0

        # Verify result structure
        from certifyai.engine.models import AttackStatus

        for r in results:
            assert r.status in (
                AttackStatus.PASS,
                AttackStatus.FAIL,
                AttackStatus.ERROR,
            )
            # Error results (rate-limited) won't have response_time
            if r.status != AttackStatus.ERROR:
                assert r.response_time_ms is not None

    @pytest.mark.asyncio
    async def test_summary_metrics(self) -> None:
        _skip_if_no_key()
        provider = _provider_config()
        config = RunConfig(
            provider=provider,
            attack_categories=[AttackCategory.PROMPT_INJECTION],
            concurrency=2,
            dry_run=False,
        )
        registry = PluginRegistry()
        runner = AttackRunner(config, registry=registry)
        summary, results = await runner.run_all()

        assert summary.total_attacks == len(results)
        total = summary.passed + summary.failed + summary.errors
        assert total == summary.total_attacks
        assert summary.overall_score is not None
        assert 0.0 <= summary.overall_score <= 1.0


# ---------------------------------------------------------------------------
# Performance tests
# ---------------------------------------------------------------------------


class TestLLMPerformance:
    """Measure basic response time (rate-limit aware)."""

    @pytest.mark.asyncio
    async def test_response_under_30s(self) -> None:
        _skip_if_no_key()
        config = _provider_config()
        client = LLMClient(config)

        import time

        try:
            start = time.monotonic()
            await client.complete("Say exactly: hello")
            elapsed = time.monotonic() - start
            assert elapsed < 30.0, f"Response took {elapsed:.1f}s"
        except LLMError as e:
            _handle_rate_limit(e)
            raise

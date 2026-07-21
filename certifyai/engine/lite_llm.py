"""LiteLLM integration layer — provider abstraction, retry, rate limiting."""

from __future__ import annotations

import logging
from typing import Any

import litellm
from litellm import acompletion

from certifyai.engine.models import ProviderConfig

logger = logging.getLogger(__name__)


class LLMClient:
    """Async LLM client wrapping LiteLLM with retry and rate limiting."""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self._semaphore: Any = None  # asyncio.Semaphore, lazily created

        litellm.drop_params = True
        litellm.telemetry = False

        if config.api_key:
            litellm.api_key = config.api_key

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Send a prompt to the configured LLM and return the response text.

        Args:
            prompt: The prompt to send.
            **kwargs: Additional completion parameters.

        Returns:
            The response text from the LLM.

        Raises:
            LLMError: If the LLM call fails after all retries.
        """
        model = f"{self.config.provider}/{self.config.model}"
        if self.config.provider == "ollama":
            model = f"ollama/{self.config.model}"

        try:
            response = await acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                api_base=self.config.endpoint,
                max_tokens=kwargs.get("max_tokens", 1024),
                temperature=kwargs.get("temperature", 0.0),
                timeout=self.config.timeout_seconds,
                num_retries=self.config.max_retries,
            )
            return response.choices[0].message.content or ""

        except litellm.APIError as e:
            raise LLMError(f"API error: {e}") from e
        except litellm.RateLimitError as e:
            raise LLMError(f"Rate limited: {e}") from e
        except litellm.Timeout as e:
            raise LLMError(f"Timeout after {self.config.timeout_seconds}s: {e}") from e
        except Exception as e:
            raise LLMError(f"Unexpected error: {e}") from e

    async def complete_batch(
        self, prompts: list[str], concurrency: int = 5
    ) -> list[tuple[str, str | None]]:
        """Send multiple prompts concurrently.

        Args:
            prompts: List of prompts to send.
            concurrency: Maximum concurrent requests.

        Returns:
            List of (prompt, response_or_error) tuples.
        """
        import asyncio

        semaphore = asyncio.Semaphore(concurrency)

        async def _bounded(p: str) -> tuple[str, str | None]:
            async with semaphore:
                try:
                    resp = await self.complete(p)
                    return p, resp
                except LLMError as e:
                    logger.warning("LLM call failed for prompt %r: %s", p[:50], e)
                    return p, None

        tasks = [_bounded(p) for p in prompts]
        return await asyncio.gather(*tasks)


class MockLLMClient:
    """Mock client for CI/testing — returns canned responses."""

    def __init__(self, responses: dict[str, str] | None = None) -> None:
        self.responses = responses or {}

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        return self.responses.get(
            prompt,
            "This is a mock response for testing purposes.",
        )

    async def complete_batch(
        self, prompts: list[str], concurrency: int = 5
    ) -> list[tuple[str, str | None]]:
        results: list[tuple[str, str | None]] = []
        for p in prompts:
            results.append((p, await self.complete(p)))
        return results


class LLMError(Exception):
    """Raised when an LLM call fails."""

    pass

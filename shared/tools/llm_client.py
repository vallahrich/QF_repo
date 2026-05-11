"""Model-agnostic LLM call wrapper supporting Azure AI Foundry and OpenAI.

Unified client used by all steps. Based on the analysis pipeline's client
with rate limiting, exponential backoff, and Azure/OpenAI routing.

Authentication priority:
    1. Azure AD (keyless) — run ``az login`` first; auto-obtains bearer token
    2. AZURE_API_KEY env var — explicit API key fallback

Usage:
    from shared.tools.llm_client import LLMClient
    client = LLMClient()
    result = client.call("gpt-5.1", "Your prompt here")

    # Simple one-shot for SLR-style calls
    result = client.simple_completion("gpt-5-mini", system="...", user="...")
"""

import os
import threading
import time
from collections import deque

import openai

from .env_loader import load_env
from .logger import get_logger

logger = get_logger("llm_client")

# Ensure env is loaded
load_env()

_AZURE_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


def _build_azure_token_provider():
    """Return a callable token provider using Azure AD (DefaultAzureCredential).

    DefaultAzureCredential tries, in order: environment variables,
    managed identity, Azure CLI (``az login``), and more.  The returned
    callable caches tokens and refreshes them automatically.
    """
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    credential = DefaultAzureCredential()
    return get_bearer_token_provider(credential, _AZURE_COGNITIVE_SCOPE)


class RateLimiter:
    """Simple sliding-window rate limiter for requests per minute."""

    def __init__(self, max_requests_per_minute: int = 4000) -> None:
        self._max_rpm = max_requests_per_minute
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def wait_if_needed(self) -> None:
        """Block until we can make another request without exceeding RPM."""
        with self._lock:
            now = time.monotonic()
            while self._timestamps and self._timestamps[0] < now - 60:
                self._timestamps.popleft()

            if len(self._timestamps) >= self._max_rpm:
                sleep_time = 60 - (now - self._timestamps[0]) + 0.1
                if sleep_time > 0:
                    logger.info(
                        "Rate limit: waiting %.1f seconds", sleep_time
                    )
                    time.sleep(sleep_time)

            self._timestamps.append(time.monotonic())


class LLMClient:
    """LLM client supporting Azure AI Foundry deployments.

    Routes to Azure OpenAI for configured deployments,
    with fallback to standard OpenAI for gpt* models.
    Implements exponential backoff (3 retries: 2s, 4s, 8s).
    """

    _MAX_RETRIES = 3
    _BASE_DELAY = 2  # seconds

    def __init__(self) -> None:
        self._azure_client: openai.AzureOpenAI | None = None
        self._openai_client: openai.OpenAI | None = None
        self._rate_limiter = RateLimiter()
        deployments = os.getenv("AZURE_DEPLOYMENTS", "")
        self._azure_deployments = set(
            d.strip() for d in deployments.split(",") if d.strip()
        )

    @property
    def azure_client(self) -> openai.AzureOpenAI:
        if self._azure_client is None:
            api_key = os.getenv("AZURE_API_KEY")
            endpoint = os.getenv("AZURE_ENDPOINT", "")
            api_version = os.getenv(
                "AZURE_API_VERSION", "2025-04-01-preview"
            )

            if api_key:
                # Explicit API key — use directly
                logger.info("Azure auth: using API key")
                self._azure_client = openai.AzureOpenAI(
                    api_key=api_key,
                    azure_endpoint=endpoint,
                    api_version=api_version,
                    timeout=300.0,
                )
            else:
                # Keyless — Azure AD via az login / managed identity
                logger.info("Azure auth: using Azure AD (keyless)")
                token_provider = _build_azure_token_provider()
                self._azure_client = openai.AzureOpenAI(
                    azure_ad_token_provider=token_provider,
                    azure_endpoint=endpoint,
                    api_version=api_version,
                    timeout=300.0,
                )
        return self._azure_client

    @property
    def openai_client(self) -> openai.OpenAI:
        if self._openai_client is None:
            # Reproducibility guard 2026-05-02: openai.OpenAI() relies on the
            # OPENAI_API_KEY env var; env_loader.py does NOT load or normalise
            # it (only AZURE_API_KEY / AZURE_OPENAI_API_KEY). Fail loudly here
            # rather than letting the constructor silently produce a client
            # that 401s on first use.
            if not os.environ.get("OPENAI_API_KEY"):
                raise RuntimeError(
                    "openai.OpenAI() fallback path requires OPENAI_API_KEY "
                    "in the environment. Set it explicitly, or route the "
                    "call through an Azure deployment listed in "
                    "AZURE_DEPLOYMENTS."
                )
            self._openai_client = openai.OpenAI()
        return self._openai_client

    def call(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        response_format: dict | None = None,
    ) -> str:
        """Call an LLM and return the response text.

        Routes to Azure for known deployment names,
        standard OpenAI for gpt* models, and Azure as default.

        Args:
            response_format: Optional. Pass {"type": "json_object"} to force JSON output.
        """
        if model in self._azure_deployments or not model.startswith("gpt"):
            call_fn = self._call_azure
        else:
            call_fn = self._call_openai

        self._rate_limiter.wait_if_needed()

        last_error: Exception | None = None
        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                start = time.monotonic()
                result = call_fn(model, prompt, temperature, max_tokens, response_format)
                elapsed = time.monotonic() - start
                # Token-usage capture (added 2026-05-02 freeze): _call_azure /
                # _call_openai stash the last response on the instance so we
                # can record usage in the same JSONL line. Best-effort —
                # absent fields default to None.
                _usage = getattr(self, "_last_usage", None) or {}
                _resp = getattr(self, "_last_response_meta", None) or {}
                logger.info(
                    "LLM call succeeded",
                    extra={
                        "model": model,
                        "model_returned": _resp.get("model"),
                        "system_fingerprint": _resp.get("system_fingerprint"),
                        "attempt": attempt,
                        "latency_s": round(elapsed, 2),
                        "prompt_len": len(prompt),
                        "response_len": len(result),
                        "prompt_tokens": _usage.get("prompt_tokens"),
                        "completion_tokens": _usage.get("completion_tokens"),
                        "total_tokens": _usage.get("total_tokens"),
                    },
                )
                return result
            except (
                openai.RateLimitError,
                openai.APIStatusError,
                openai.APITimeoutError,  # reproducibility-parity 2026-05-02
                                          # (was missing here; simple_completion already retries on it)
            ) as exc:
                last_error = exc
                delay = self._BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "LLM call failed, retrying",
                    extra={
                        "model": model,
                        "attempt": attempt,
                        "error": str(exc),
                        "retry_delay_s": delay,
                    },
                )
                time.sleep(delay)

        raise RuntimeError(
            f"LLM call to {model} failed after {self._MAX_RETRIES} retries: "
            f"{last_error}"
        )

    # Model families that only accept temperature=1 (reasoning models)
    _REASONING_PREFIXES = ("o1", "o3", "o4", "gpt-5-mini", "gpt-5.1", "gpt-5.2", "gpt-5.3")

    # Reproducibility guard 2026-05-02: warn-once-per-(process, model) when a
    # caller-supplied temperature is silently dropped because the target model
    # is in _REASONING_PREFIXES. Several extraction_config.json files specify
    # `temperature: 0.1..0.3` for `gpt-5.1` / `gpt-5-mini` and assume
    # determinism that the API path cannot deliver.
    _temperature_drop_warned: set[str] = set()

    @staticmethod
    def _is_reasoning_model(model: str) -> bool:
        """Check if a model is a reasoning model that doesn't support temperature."""
        return any(model.startswith(p) for p in LLMClient._REASONING_PREFIXES)

    @classmethod
    def _maybe_warn_temperature_dropped(cls, model: str, temperature: float) -> None:
        """Emit a one-time WARNING when a reasoning model drops a non-default temperature."""
        if temperature == 1.0 or model in cls._temperature_drop_warned:
            return
        cls._temperature_drop_warned.add(model)
        import warnings
        warnings.warn(
            f"LLMClient: dropping temperature={temperature} for reasoning model "
            f"'{model}' (reasoning models accept only temperature=1). Any prior "
            f"determinism assumption from a config file is incorrect for this model.",
            RuntimeWarning,
            stacklevel=3,
        )
        logger.warning(
            "LLMClient temperature dropped for reasoning model",
            extra={"model": model, "requested_temperature": temperature},
        )

    def simple_completion(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        timeout: float = 300,
    ) -> str:
        """System + user message completion (SLR-style calling pattern).

        Wraps the two-message pattern used by the SLR toolkit.
        Automatically omits temperature for reasoning models.

        Args:
            timeout: Maximum seconds to wait for a response (default 300s / 5min).
        """
        self._rate_limiter.wait_if_needed()

        # Build kwargs — reasoning models don't support temperature
        kwargs: dict = {
            "model": model,
            "max_completion_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if not self._is_reasoning_model(model):
            kwargs["temperature"] = temperature
        else:
            self._maybe_warn_temperature_dropped(model, temperature)

        last_error: Exception | None = None
        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                response = self.azure_client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                if content is None:
                    raise RuntimeError(
                        f"Model {model} returned no content "
                        f"(finish_reason={response.choices[0].finish_reason})"
                    )
                # Reproducibility log 2026-05-02: record OpenAI's per-response
                # model + system_fingerprint so reruns can be cross-checked.
                logger.info(
                    "simple_completion succeeded",
                    extra={
                        "model_requested": model,
                        "model_returned": getattr(response, "model", None),
                        "system_fingerprint": getattr(response, "system_fingerprint", None),
                        "attempt": attempt,
                        "response_len": len(content),
                    },
                )
                return content
            except (
                openai.RateLimitError,
                openai.APIStatusError,
                openai.APITimeoutError,
            ) as exc:
                last_error = exc
                delay = self._BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "simple_completion failed, retrying",
                    extra={
                        "model": model,
                        "attempt": attempt,
                        "error": str(exc),
                        "retry_delay_s": delay,
                    },
                )
                time.sleep(delay)

        raise RuntimeError(
            f"simple_completion to {model} failed after {self._MAX_RETRIES} "
            f"retries: {last_error}"
        )

    def _call_azure(
        self, model: str, prompt: str, temperature: float, max_tokens: int,
        response_format: dict | None = None,
    ) -> str:
        kwargs: dict = {
            "model": model,
            "max_completion_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if not self._is_reasoning_model(model):
            kwargs["temperature"] = temperature
        else:
            self._maybe_warn_temperature_dropped(model, temperature)
        if response_format:
            kwargs["response_format"] = response_format
        response = self.azure_client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError(
                f"Model {model} returned no content "
                f"(finish_reason={response.choices[0].finish_reason}). "
                "This may happen with reasoning models that exhaust tokens "
                "on thinking."
            )
        # Reproducibility log 2026-05-02: see simple_completion for rationale.
        # Stash usage + response meta for the outer call() to log atomically.
        _u = getattr(response, "usage", None)
        self._last_usage = {
            "prompt_tokens": getattr(_u, "prompt_tokens", None),
            "completion_tokens": getattr(_u, "completion_tokens", None),
            "total_tokens": getattr(_u, "total_tokens", None),
        } if _u is not None else None
        self._last_response_meta = {
            "model": getattr(response, "model", None),
            "system_fingerprint": getattr(response, "system_fingerprint", None),
        }
        logger.info(
            "_call_azure response metadata",
            extra={
                "model_requested": model,
                "model_returned": getattr(response, "model", None),
                "system_fingerprint": getattr(response, "system_fingerprint", None),
            },
        )
        return content

    def _call_openai(
        self, model: str, prompt: str, temperature: float, max_tokens: int,
        response_format: dict | None = None,
    ) -> str:
        kwargs: dict = {
            "model": model,
            "max_completion_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if not self._is_reasoning_model(model):
            kwargs["temperature"] = temperature
        else:
            self._maybe_warn_temperature_dropped(model, temperature)
        if response_format:
            kwargs["response_format"] = response_format
        response = self.openai_client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError(
                f"Model {model} returned no content "
                f"(finish_reason={response.choices[0].finish_reason})"
            )
        # Reproducibility log 2026-05-02: see simple_completion for rationale.
        # Stash usage + response meta for the outer call() to log atomically.
        _u = getattr(response, "usage", None)
        self._last_usage = {
            "prompt_tokens": getattr(_u, "prompt_tokens", None),
            "completion_tokens": getattr(_u, "completion_tokens", None),
            "total_tokens": getattr(_u, "total_tokens", None),
        } if _u is not None else None
        self._last_response_meta = {
            "model": getattr(response, "model", None),
            "system_fingerprint": getattr(response, "system_fingerprint", None),
        }
        logger.info(
            "_call_openai response metadata",
            extra={
                "model_requested": model,
                "model_returned": getattr(response, "model", None),
                "system_fingerprint": getattr(response, "system_fingerprint", None),
            },
        )
        return content

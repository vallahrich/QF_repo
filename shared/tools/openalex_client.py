"""OpenAlex API client with caching and rate limiting."""

import hashlib
import json
import os
import time
from pathlib import Path

import requests

from .logger import get_logger
from ._paths import find_project_root as _find_project_root

logger = get_logger("openalex_client")


class OpenAlexTransportError(RuntimeError):
    """Raised when an OpenAlex request fails after all retries for a transport-
    layer reason (5xx, network error). Distinguishes a *transport failure* from
    a *not-found* result (which still returns None). Added 2026-05-02.

    Callers that historically treated `None` as 'no data' should catch this
    explicitly and surface the failure rather than silently substituting an
    empty list.
    """


class OpenAlexClient:
    """Client for the OpenAlex API with local JSON caching and rate limiting.

    Parameters
    ----------
    email : str | None
        If provided, added as ``mailto`` parameter for the polite pool.
    cache_dir : str | None
        Override the default cache directory.
    """

    BASE_URL = "https://api.openalex.org"
    REQUEST_INTERVAL = 0.1  # seconds between requests (10 req/s)
    MAX_RETRIES = 3
    BATCH_SIZE = 50  # max IDs per filter query

    def __init__(self, email: str | None = None, cache_dir: str | None = None) -> None:
        self._email = email
        root = _find_project_root()
        self._cache_dir = cache_dir or str(root / "openalex_cache")
        os.makedirs(self._cache_dir, exist_ok=True)
        self._last_request_time: float = 0.0
        self._session = requests.Session()

    def get_work_by_doi(self, doi: str) -> dict | None:
        """Fetch an OpenAlex work record by DOI."""
        normalized = self._normalize_doi(doi)
        if not normalized:
            return None

        cached = self._read_cache(f"doi_{normalized}")
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}/works/https://doi.org/{normalized}"
        data = self._get(url)
        if data is not None:
            self._write_cache(f"doi_{normalized}", data)
        return data

    def get_references(self, doi: str) -> list[str]:
        """Return DOIs of works referenced by the given paper."""
        work = self.get_work_by_doi(doi)
        if not work:
            return []

        ref_ids = work.get("referenced_works", [])
        if not ref_ids:
            return []

        resolved = self.resolve_openalex_ids(ref_ids)
        return [r["doi"] for r in resolved if r.get("doi")]

    def get_cited_by_count(self, doi: str) -> int:
        """Return the global cited-by count for a paper, or 0 if unknown."""
        work = self.get_work_by_doi(doi)
        if not work:
            return 0
        return work.get("cited_by_count", 0)

    def resolve_openalex_ids(self, ids: list[str]) -> list[dict]:
        """Resolve a list of OpenAlex work IDs to basic metadata."""
        results: list[dict] = []
        for i in range(0, len(ids), self.BATCH_SIZE):
            batch = ids[i : i + self.BATCH_SIZE]
            batch_results = self._resolve_batch(batch)
            results.extend(batch_results)
        return results

    def _resolve_batch(self, ids: list[str]) -> list[dict]:
        """Resolve a single batch of OpenAlex IDs (≤50)."""
        cache_key = self._batch_cache_key(ids)
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached

        short_ids = []
        for oa_id in ids:
            short = oa_id.rsplit("/", 1)[-1] if "/" in oa_id else oa_id
            short_ids.append(short)

        filter_val = "|".join(short_ids)
        url = f"{self.BASE_URL}/works"
        params: dict = {
            "filter": f"openalex:{filter_val}",
            "per_page": 200,
            "select": "id,doi,display_name,publication_year,authorships",
        }
        data = self._get(url, params=params)
        if data is None:
            return []

        results = []
        for work in data.get("results", []):
            doi_raw = work.get("doi") or ""
            doi_clean = (
                doi_raw.replace("https://doi.org/", "").strip()
                if doi_raw
                else ""
            )
            authorships = work.get("authorships", [])
            first_author = ""
            if authorships:
                author_obj = authorships[0].get("author", {})
                first_author = author_obj.get("display_name", "")
            results.append(
                {
                    "openalex_id": work.get("id", ""),
                    "doi": doi_clean,
                    "title": work.get("display_name", ""),
                    "year": work.get("publication_year"),
                    "first_author": first_author,
                }
            )

        self._write_cache(cache_key, results)
        return results

    def _get(self, url: str, params: dict | None = None) -> dict | None:
        """HTTP GET with rate limiting and retry on 429 / 5xx.

        Returns:
            dict on 200, None on 404.
        Raises:
            OpenAlexTransportError: persistent 5xx or network failure after
            MAX_RETRIES attempts. Previously this returned None silently,
            indistinguishable from a 404. Reproducibility guard 2026-05-02.
        """
        if params is None:
            params = {}
        if self._email:
            params["mailto"] = self._email

        last_status: int | None = None
        last_exc: BaseException | None = None
        for attempt in range(self.MAX_RETRIES):
            self._rate_limit()
            try:
                resp = self._session.get(url, params=params, timeout=30)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 429:
                    wait = 2**attempt
                    logger.warning(
                        "Rate limited (429), retrying in %ds (attempt %d/%d)",
                        wait,
                        attempt + 1,
                        self.MAX_RETRIES,
                    )
                    time.sleep(wait)
                    continue
                if resp.status_code == 404:
                    logger.debug("Not found (404): %s", url)
                    return None
                if 500 <= resp.status_code < 600:
                    last_status = resp.status_code
                    wait = 2**attempt
                    logger.warning(
                        "Server error %d for %s, retrying in %ds (attempt %d/%d)",
                        resp.status_code, url, wait, attempt + 1, self.MAX_RETRIES,
                    )
                    time.sleep(wait)
                    continue
                # 4xx other than 404/429: do not retry; surface as transport error.
                raise OpenAlexTransportError(
                    f"OpenAlex returned HTTP {resp.status_code} for {url}"
                )
            except requests.RequestException as exc:
                last_exc = exc
                logger.warning("Request error for %s: %s", url, exc)
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2**attempt)
                    continue
                raise OpenAlexTransportError(
                    f"OpenAlex network failure for {url} after {self.MAX_RETRIES} "
                    f"retries: {exc}"
                ) from exc
        # Loop exhausted on retryable status (5xx or 429)
        raise OpenAlexTransportError(
            f"OpenAlex retries exhausted for {url}; last_status={last_status}"
        )

    def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self.REQUEST_INTERVAL:
            time.sleep(self.REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.monotonic()

    @staticmethod
    def _normalize_doi(doi: str) -> str:
        """Strip common prefixes and lowercase a DOI."""
        doi = doi.strip()
        for prefix in (
            "https://doi.org/",
            "http://doi.org/",
            "https://dx.doi.org/",
            "http://dx.doi.org/",
        ):
            if doi.lower().startswith(prefix):
                doi = doi[len(prefix) :]
                break
        return doi.lower()

    @staticmethod
    def _batch_cache_key(ids: list[str]) -> str:
        """Deterministic cache key for a batch of OpenAlex IDs."""
        joined = "|".join(sorted(ids))
        digest = hashlib.sha256(joined.encode()).hexdigest()[:16]
        return f"batch_{digest}"

    def _cache_path(self, key: str) -> str:
        safe_key = key.replace("/", "_").replace(":", "_")
        return os.path.join(self._cache_dir, f"{safe_key}.json")

    def _read_cache(self, key: str) -> dict | list | None:
        path = self._cache_path(key)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.debug("Cache read error for %s: %s", key, exc)
            return None

    def _write_cache(self, key: str, data: dict | list) -> None:
        path = self._cache_path(key)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as exc:
            logger.debug("Cache write error for %s: %s", key, exc)

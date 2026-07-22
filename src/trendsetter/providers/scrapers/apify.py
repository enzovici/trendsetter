"""Apify adapter (fallback scraper).

Uses Apify's run-sync API: POST /v2/acts/{actor_id}/run-sync-get-dataset-items
which returns the dataset items as a JSON array. Item shapes are defined by
tests/fixtures/apify/*.json. Those fixtures are ASSUMED shapes until re-recorded
against the live actors with scripts/record_fixture.py — if an actor's real
output differs, fix the fixture and the parser together. Parsing reuses the
tolerant `parse_post` from the scrapecreators module.
"""

from typing import Any

import httpx

from trendsetter.config import get_settings
from trendsetter.db.models import Platform
from trendsetter.providers.base import (
    Capability,
    FetchRequest,
    ProviderError,
    ProviderResult,
    normalize_hashtag,
)
from trendsetter.providers.scrapers.scrapecreators import parse_post

ACTORS: dict[tuple[Platform, Capability], str] = {
    (Platform.tiktok, Capability.HASHTAG_POSTS): "clockworks~tiktok-scraper",
    (Platform.tiktok, Capability.PROFILE_POSTS): "clockworks~tiktok-scraper",
    (Platform.instagram, Capability.HASHTAG_POSTS): "apify~instagram-hashtag-scraper",
    (Platform.instagram, Capability.PROFILE_POSTS): "apify~instagram-scraper",
}


def _actor_input(req: FetchRequest) -> dict[str, Any]:
    limit = int(req.params.get("limit", 20))
    if req.capability is Capability.HASHTAG_POSTS:
        tag = normalize_hashtag(req.params.get("hashtag", ""))
        if req.platform is Platform.tiktok:
            return {"hashtags": [tag], "resultsPerPage": limit}
        return {"hashtags": [tag], "resultsLimit": limit}
    handle = req.params.get("profile_id", "")
    if req.platform is Platform.tiktok:
        return {"profiles": [handle], "resultsPerPage": limit}
    return {"directUrls": [f"https://www.instagram.com/{handle}/"], "resultsLimit": limit}


class ApifyAdapter:
    provider_id = "apify"
    platforms = frozenset({Platform.tiktok, Platform.instagram})
    capabilities = frozenset({Capability.HASHTAG_POSTS, Capability.PROFILE_POSTS})

    def __init__(
        self,
        base_url: str,
        cost_per_item_usd: dict[str, float],
        client: httpx.AsyncClient | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.cost_per_item_usd = cost_per_item_usd
        self._client = client

    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120)
        return self._client

    async def fetch(self, req: FetchRequest) -> ProviderResult:
        actor_id = ACTORS.get((req.platform, req.capability))
        if actor_id is None:
            raise ProviderError(
                f"apify does not support ({req.platform.value}, {req.capability.value})"
            )
        url = f"{self.base_url}/v2/acts/{actor_id}/run-sync-get-dataset-items"

        try:
            resp = await self._http().post(
                url, params={"token": get_settings().apify_token}, json=_actor_input(req)
            )
        except httpx.HTTPError as exc:
            raise ProviderError(f"apify request failed: {exc}") from exc
        if resp.status_code == 429:
            raise ProviderError("apify rate-limited (429)")
        if resp.status_code >= 400:
            raise ProviderError(f"apify HTTP {resp.status_code}: {resp.text[:200]}")
        body = resp.json()

        items = [i for i in body if isinstance(i, dict)] if isinstance(body, list) else []
        posts = [p for p in (parse_post(req.platform, i) for i in items) if p is not None]

        return ProviderResult(
            provider=self.provider_id,
            posts=posts,
            credits_used=float(len(items)),
            est_cost_usd=len(items) * self.cost_per_item_usd.get(req.platform.value, 0.0),
            meta={"status_code": resp.status_code, "actor_id": actor_id},
        )

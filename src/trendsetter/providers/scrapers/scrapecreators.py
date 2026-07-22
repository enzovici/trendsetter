"""ScrapeCreators adapter (primary scraper).

Endpoint paths and response shapes are defined by tests/fixtures/scrapecreators/*.json.
Those fixtures are ASSUMED shapes until re-recorded against the live API with
scripts/record_fixture.py — if the vendor's real schema differs, fix the fixture
and the parser together. The parser is deliberately tolerant of key naming.
"""

from datetime import UTC, datetime
from typing import Any

import httpx

from trendsetter.config import get_settings
from trendsetter.db.models import EntityType, Platform
from trendsetter.providers.base import (
    Capability,
    FetchRequest,
    ProviderError,
    ProviderResult,
    RawEntity,
    RawPost,
    normalize_hashtag,
)

ENDPOINTS: dict[tuple[Platform, Capability], str] = {
    (Platform.tiktok, Capability.HASHTAG_POSTS): "/v1/tiktok/hashtag",
    (Platform.tiktok, Capability.PROFILE_POSTS): "/v1/tiktok/profile/videos",
    (Platform.tiktok, Capability.TRENDING_FEED): "/v1/tiktok/trending",
    (Platform.instagram, Capability.HASHTAG_POSTS): "/v1/instagram/hashtag",
    (Platform.instagram, Capability.PROFILE_POSTS): "/v1/instagram/user/posts",
}


def _first(item: dict, *keys: str, default=None):
    for k in keys:
        if k in item and item[k] is not None:
            return item[k]
    return default


def _parse_created_at(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_post(platform: Platform, item: dict[str, Any]) -> RawPost | None:
    external_id = _first(item, "id", "aweme_id", "video_id", "pk", "code")
    if external_id is None:
        return None
    text = _first(item, "text", "desc", "caption", "title", default="") or ""
    author = _first(item, "author", "user", "owner", "authorMeta", default={}) or {}
    if isinstance(author, str):
        author = {"unique_id": author}
    # Flat author fallbacks (Apify instagram actors emit ownerUsername/ownerId).
    if not author:
        author = {"unique_id": _first(item, "ownerUsername"), "id": _first(item, "ownerId")}
    stats = _first(item, "stats", "statistics", "metrics", default={}) or {}
    metrics = {}
    for out_key, keys in {
        "views": ("play_count", "view_count", "views", "playCount", "videoViewCount", "viewCount"),
        "likes": ("digg_count", "like_count", "likes", "diggCount", "likesCount"),
        "comments": ("comment_count", "comments", "commentCount", "commentsCount"),
        "shares": ("share_count", "shares", "shareCount", "sharesCount"),
    }.items():
        v = _first(stats, *keys) or _first(item, *keys)
        if v is not None:
            metrics[out_key] = int(v)
    hashtags = [
        normalize_hashtag(h if isinstance(h, str) else _first(h, "name", "title", default=""))
        for h in (_first(item, "hashtags", "challenges", "text_extra", default=[]) or [])
    ]
    hashtags = [h for h in hashtags if h]
    music = _first(item, "music", "sound", "audio", default={}) or {}
    sounds = [str(_first(music, "id", "music_id", default=""))] if music else []
    sounds = [s for s in sounds if s]
    return RawPost(
        platform=platform,
        external_id=str(external_id),
        author_external_id=(
            str(_first(author, "id", "uid", "user_id")) if _first(author, "id", "uid", "user_id") else None
        ),
        author_handle=_first(author, "unique_id", "username", "uniqueId", "handle"),
        text=text,
        url=_first(item, "url", "share_url", "permalink", "web_video_url", "webVideoUrl"),
        created_at=_parse_created_at(_first(item, "create_time", "created_at", "taken_at", "createTime")),
        metrics=metrics,
        hashtags=hashtags,
        sounds=sounds,
        media_kind=_first(item, "media_kind", "media_type", default="video"),
        raw=item,
    )


class ScrapeCreatorsAdapter:
    provider_id = "scrapecreators"
    platforms = frozenset({Platform.tiktok, Platform.instagram})
    capabilities = frozenset(
        {Capability.HASHTAG_POSTS, Capability.PROFILE_POSTS, Capability.TRENDING_FEED}
    )

    def __init__(self, base_url: str, cost_per_call_usd: float, client: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.cost_per_call_usd = cost_per_call_usd
        self._client = client

    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"x-api-key": get_settings().scrapecreators_api_key}, timeout=30
            )
        return self._client

    async def fetch(self, req: FetchRequest) -> ProviderResult:
        path = ENDPOINTS.get((req.platform, req.capability))
        if path is None:
            raise ProviderError(
                f"scrapecreators does not support ({req.platform.value}, {req.capability.value})"
            )
        params: dict[str, Any] = {}
        if "hashtag" in req.params:
            params["hashtag"] = normalize_hashtag(req.params["hashtag"])
        if "profile_id" in req.params:
            params["handle"] = req.params["profile_id"]
        if "limit" in req.params:
            params["count"] = req.params["limit"]
        if "cursor" in req.params and req.params["cursor"]:
            params["cursor"] = req.params["cursor"]

        try:
            resp = await self._http().get(self.base_url + path, params=params)
        except httpx.HTTPError as exc:
            raise ProviderError(f"scrapecreators request failed: {exc}") from exc
        if resp.status_code == 429:
            raise ProviderError("scrapecreators rate-limited (429)")
        if resp.status_code >= 400:
            raise ProviderError(f"scrapecreators HTTP {resp.status_code}: {resp.text[:200]}")
        body = resp.json()

        items = body.get("posts") or body.get("videos") or body.get("items") or body.get("data") or []
        posts = [p for p in (parse_post(req.platform, i) for i in items) if p is not None]

        entities: list[RawEntity] = []
        if req.capability is Capability.TRENDING_FEED:
            for rank, t in enumerate(body.get("trends") or body.get("hashtags") or [], start=1):
                name = t if isinstance(t, str) else _first(t, "name", "hashtag", "title")
                if name:
                    entities.append(
                        RawEntity(
                            platform=req.platform,
                            entity_type=EntityType.hashtag,
                            natural_key=normalize_hashtag(name),
                            display_name=name if isinstance(name, str) else None,
                            rank=rank,
                            meta=t if isinstance(t, dict) else {},
                        )
                    )

        return ProviderResult(
            provider=self.provider_id,
            posts=posts,
            entities=entities,
            cursor=body.get("cursor") or body.get("next_cursor"),
            credits_used=float(body.get("credits_used", 1)),
            est_cost_usd=float(body.get("credits_used", 1)) * self.cost_per_call_usd,
            meta={"status_code": resp.status_code},
        )

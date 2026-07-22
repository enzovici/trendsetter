"""Provider abstraction: capability-based adapter protocol + normalized data contracts.

Adapters NEVER touch the database — they turn vendor responses into RawPost/RawEntity.
`ingest.normalize` is the only writer.
"""

import enum
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from trendsetter.db.models import EntityType, Platform


class Capability(enum.StrEnum):
    TRENDING_FEED = "trending_feed"
    HASHTAG_POSTS = "hashtag_posts"
    KEYWORD_SEARCH = "keyword_search"
    PROFILE_POSTS = "profile_posts"
    SOUND_POSTS = "sound_posts"
    OWN_INSIGHTS = "own_insights"
    PUBLISH = "publish"


class ProviderError(RuntimeError):
    """Adapter-level failure (bad response, upstream 5xx). Registry falls through."""


class QuotaExceededError(ProviderError):
    """Platform-side quota hit (e.g. IG 30-hashtags/7d). Registry falls through."""


class RawPost(BaseModel):
    platform: Platform
    external_id: str
    author_external_id: str | None = None
    author_handle: str | None = None
    text: str | None = None
    lang: str | None = None
    url: str | None = None
    created_at: datetime | None = None
    metrics: dict[str, int | float] = Field(default_factory=dict)
    hashtags: list[str] = Field(default_factory=list)
    sounds: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)
    media_kind: str | None = None  # video|image|carousel
    raw: dict[str, Any] = Field(default_factory=dict)


class RawEntity(BaseModel):
    platform: Platform
    entity_type: EntityType
    natural_key: str
    display_name: str | None = None
    rank: int | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class FetchRequest(BaseModel):
    platform: Platform
    capability: Capability
    # Capability-specific params: hashtag, keyword, profile_id, sound_id, limit, cursor...
    params: dict[str, Any] = Field(default_factory=dict)


class ProviderResult(BaseModel):
    provider: str
    posts: list[RawPost] = Field(default_factory=list)
    entities: list[RawEntity] = Field(default_factory=list)
    cursor: str | None = None
    # What the adapter believes this call cost (ledger uses this).
    credits_used: float = 1.0
    est_cost_usd: float = 0.0
    meta: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class ProviderAdapter(Protocol):
    provider_id: str
    platforms: frozenset[Platform]
    capabilities: frozenset[Capability]

    async def fetch(self, req: FetchRequest) -> ProviderResult: ...


def normalize_hashtag(tag: str) -> str:
    return tag.strip().lstrip("#").lower()

"""Polling collectors. M0: manual hashtag pull. M1 adds scheduled trending/watchlist jobs."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from trendsetter.config import load_yaml
from trendsetter.db.models import Platform
from trendsetter.ingest.normalize import IngestStats, ingest_posts, ingest_trend_entities
from trendsetter.providers.base import Capability, FetchRequest
from trendsetter.providers.registry import ProviderRegistry

log = logging.getLogger(__name__)


async def pull_hashtag(
    session: AsyncSession,
    registry: ProviderRegistry,
    platform: Platform,
    hashtag: str,
    limit: int | None = None,
    tenant_id=None,
) -> IngestStats:
    limit = limit or load_yaml("cadence.yml")["limits"]["posts_per_hashtag_pull"]
    result = await registry.fetch_with_fallback(
        session,
        FetchRequest(
            platform=platform,
            capability=Capability.HASHTAG_POSTS,
            params={"hashtag": hashtag, "limit": limit},
        ),
        tenant_id=tenant_id,
    )
    stats = await ingest_posts(session, result.posts, source_provider=result.provider, tenant_id=tenant_id)
    log.info(
        "pulled #%s (%s): %d events, %d new items, %d entities",
        hashtag, platform.value, stats.events, stats.new_content_items, len(stats.entities_touched),
    )
    return stats


async def pull_trending(
    session: AsyncSession,
    registry: ProviderRegistry,
    platform: Platform,
    tenant_id=None,
) -> int:
    result = await registry.fetch_with_fallback(
        session,
        FetchRequest(platform=platform, capability=Capability.TRENDING_FEED, params={}),
        tenant_id=tenant_id,
    )
    if result.posts:
        await ingest_posts(session, result.posts, source_provider=result.provider, tenant_id=tenant_id)
    entities = await ingest_trend_entities(session, result.entities)
    log.info("trending (%s): %d entities, %d posts", platform.value, len(entities), len(result.posts))
    return len(entities)

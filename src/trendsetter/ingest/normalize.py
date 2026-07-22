"""Sole writer of events/content_items/entities. Adapters return RawPost/RawEntity;
this module turns them into rows.

Upserts are select-then-insert (not ON CONFLICT) deliberately: portable to sqlite
for tests, and MVP volumes make the race window irrelevant (single worker process).
"""

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from trendsetter.db.models import (
    ContentItem,
    Entity,
    EntityType,
    Event,
    EventEntity,
    Platform,
)
from trendsetter.providers.base import RawEntity, RawPost


@dataclass
class IngestStats:
    events: int = 0
    new_content_items: int = 0
    entities_touched: set[str] = field(default_factory=set)


async def get_or_create_entity(
    session: AsyncSession,
    platform: Platform,
    entity_type: EntityType,
    natural_key: str,
    display_name: str | None = None,
    meta: dict | None = None,
) -> Entity:
    result = await session.execute(
        sa.select(Entity).where(
            Entity.platform == platform,
            Entity.entity_type == entity_type,
            Entity.natural_key == natural_key,
        )
    )
    entity = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if entity is None:
        entity = Entity(
            platform=platform,
            entity_type=entity_type,
            natural_key=natural_key,
            display_name=display_name or natural_key,
            meta=meta,
            first_seen=now,
            last_seen=now,
        )
        session.add(entity)
        await session.flush()
    else:
        entity.last_seen = now
    return entity


async def ingest_posts(
    session: AsyncSession,
    posts: list[RawPost],
    source_provider: str,
    tenant_id=None,
) -> IngestStats:
    stats = IngestStats()
    now = datetime.now(UTC)
    for post in posts:
        result = await session.execute(
            sa.select(ContentItem).where(
                ContentItem.platform == post.platform,
                ContentItem.external_id == post.external_id,
            )
        )
        item = result.scalar_one_or_none()
        is_first = item is None
        if is_first:
            item = ContentItem(
                platform=post.platform,
                external_id=post.external_id,
                author_external_id=post.author_external_id,
                author_handle=post.author_handle,
                first_seen_at=now,
                text_hash=hashlib.sha256((post.text or "").encode()).hexdigest(),
            )
            session.add(item)
            await session.flush()
            stats.new_content_items += 1

        event = Event(
            event_time=now,
            platform=post.platform,
            source_provider=source_provider,
            event_kind=post.media_kind or "post",
            content_item_id=item.id,
            external_id=post.external_id,
            author_external_id=post.author_external_id,
            text=post.text,
            lang=post.lang,
            url=post.url,
            metrics=dict(post.metrics) if post.metrics else None,
            is_first_observation=is_first,
            tenant_id=tenant_id,
        )
        session.add(event)
        await session.flush()
        stats.events += 1

        entity_specs: list[tuple[EntityType, str]] = [
            (EntityType.hashtag, h) for h in post.hashtags
        ]
        entity_specs += [(EntityType.sound, s) for s in post.sounds]
        if post.author_handle:
            entity_specs.append((EntityType.creator, post.author_handle.lower()))
        seen: set[tuple[EntityType, str]] = set()
        for entity_type, key in entity_specs:
            if not key or (entity_type, key) in seen:
                continue
            seen.add((entity_type, key))
            entity = await get_or_create_entity(session, post.platform, entity_type, key)
            session.add(
                EventEntity(
                    event_id=event.id,
                    event_time=event.event_time,
                    entity_id=entity.id,
                    is_first_observation=is_first,
                )
            )
            stats.entities_touched.add(f"{entity_type.value}:{key}")
    await session.commit()
    return stats


async def ingest_trend_entities(
    session: AsyncSession, entities: list[RawEntity]
) -> list[Entity]:
    """Record trending-feed entities (creates them if unseen; ranks kept in meta)."""
    rows: list[Entity] = []
    for raw in entities:
        entity = await get_or_create_entity(
            session,
            raw.platform,
            raw.entity_type,
            raw.natural_key,
            display_name=raw.display_name,
            meta={**raw.meta, "last_trending_rank": raw.rank} if raw.rank else raw.meta,
        )
        rows.append(entity)
    await session.commit()
    return rows

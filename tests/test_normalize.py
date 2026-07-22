import sqlalchemy as sa

from trendsetter.db.models import ContentItem, Entity, EntityType, Event, Platform
from trendsetter.ingest.normalize import ingest_posts, ingest_trend_entities
from trendsetter.providers.base import RawEntity, RawPost


def make_posts() -> list[RawPost]:
    return [
        RawPost(
            platform=Platform.tiktok,
            external_id="post-1",
            author_external_id="u1",
            author_handle="LiftLaura",
            text="leg day #fitness",
            metrics={"views": 1000, "likes": 50},
            hashtags=["fitness"],
            sounds=["sound-1"],
        ),
        RawPost(
            platform=Platform.tiktok,
            external_id="post-2",
            text="shred update #fitness",
            metrics={"views": 500},
            hashtags=["fitness"],
        ),
    ]


async def test_ingest_posts_creates_events_and_entities(sqlite_session):
    stats = await ingest_posts(sqlite_session, make_posts(), source_provider="scrapecreators")
    assert stats.events == 2
    assert stats.new_content_items == 2
    assert "hashtag:fitness" in stats.entities_touched

    hashtags = (
        (
            await sqlite_session.execute(
                sa.select(Entity).where(
                    Entity.entity_type == EntityType.hashtag,
                    Entity.natural_key == "fitness",
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(hashtags) == 1

    creators = (
        (
            await sqlite_session.execute(
                sa.select(Entity).where(
                    Entity.entity_type == EntityType.creator,
                    Entity.natural_key == "liftlaura",
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(creators) == 1


async def test_reingest_dedupes_content_items_but_appends_events(sqlite_session):
    posts = make_posts()
    first = await ingest_posts(sqlite_session, posts, source_provider="scrapecreators")
    assert first.new_content_items == 2

    second = await ingest_posts(sqlite_session, posts, source_provider="scrapecreators")
    assert second.new_content_items == 0
    assert second.events == 2

    total_events = (
        await sqlite_session.execute(sa.select(sa.func.count()).select_from(Event))
    ).scalar_one()
    assert total_events == 4

    repeat_events = (
        await sqlite_session.execute(
            sa.select(sa.func.count())
            .select_from(Event)
            .where(Event.is_first_observation.is_(False))
        )
    ).scalar_one()
    assert repeat_events == 2

    total_items = (
        await sqlite_session.execute(sa.select(sa.func.count()).select_from(ContentItem))
    ).scalar_one()
    assert total_items == 2


async def test_ingest_trend_entities_records_rank(sqlite_session):
    raws = [
        RawEntity(
            platform=Platform.tiktok,
            entity_type=EntityType.hashtag,
            natural_key="grwm",
            display_name="grwm",
            rank=1,
        ),
        RawEntity(
            platform=Platform.tiktok,
            entity_type=EntityType.hashtag,
            natural_key="fittok",
            display_name="fittok",
            rank=2,
        ),
    ]
    entities = await ingest_trend_entities(sqlite_session, raws)
    assert len(entities) == 2
    assert entities[0].meta["last_trending_rank"] == 1
    assert entities[1].meta["last_trending_rank"] == 2

    stored = (
        (
            await sqlite_session.execute(
                sa.select(Entity).where(Entity.entity_type == EntityType.hashtag)
            )
        )
        .scalars()
        .all()
    )
    assert {e.natural_key for e in stored} == {"grwm", "fittok"}

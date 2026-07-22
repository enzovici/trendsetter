import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Portable JSON: JSONB on Postgres, plain JSON elsewhere (sqlite in tests).
JSONVariant = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

EMBEDDING_DIM = 1536


class Base(DeclarativeBase):
    pass


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)


def _now() -> Mapped[datetime]:
    return mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())


class Platform(enum.StrEnum):
    tiktok = "tiktok"
    instagram = "instagram"


class EntityType(enum.StrEnum):
    hashtag = "hashtag"
    sound = "sound"
    keyword = "keyword"
    creator = "creator"
    topic = "topic"


class WatchTier(enum.StrEnum):
    hot = "hot"
    standard = "standard"
    slow = "slow"


class BurstState(enum.StrEnum):
    candidate = "candidate"
    active = "active"
    ended = "ended"
    dismissed = "dismissed"


class PlanStatus(enum.StrEnum):
    idea = "idea"
    drafting = "drafting"
    approved = "approved"
    scheduled = "scheduled"
    published = "published"
    failed = "failed"


class DraftStatus(enum.StrEnum):
    proposed = "proposed"
    edited = "edited"
    approved = "approved"
    rejected = "rejected"


class PublishStatus(enum.StrEnum):
    pending = "pending"
    processing = "processing"
    published = "published"
    failed = "failed"


# --------------------------------------------------------------------------
# Tenant-scoped tables
# --------------------------------------------------------------------------


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = _now()


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tenants.id"))
    platform: Mapped[Platform] = mapped_column(sa.Enum(Platform, native_enum=False))
    handle: Mapped[str] = mapped_column(sa.Text)
    kind: Mapped[str] = mapped_column(sa.Text, default="owned")  # owned|competitor|watch
    external_user_id: Mapped[str | None] = mapped_column(sa.Text)
    access_token_enc: Mapped[bytes | None] = mapped_column(sa.LargeBinary)
    refresh_token_enc: Mapped[bytes | None] = mapped_column(sa.LargeBinary)
    token_expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    scopes: Mapped[list | None] = mapped_column(JSONVariant)
    status: Mapped[str] = mapped_column(sa.Text, default="active")
    created_at: Mapped[datetime] = _now()

    __table_args__ = (sa.UniqueConstraint("tenant_id", "platform", "handle"),)


class Watchlist(Base):
    __tablename__ = "watchlist"

    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tenants.id"))
    entity_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("entities.id"))
    tier: Mapped[WatchTier] = mapped_column(
        sa.Enum(WatchTier, native_enum=False), default=WatchTier.standard
    )
    notes: Mapped[str | None] = mapped_column(sa.Text)
    added_at: Mapped[datetime] = _now()

    __table_args__ = (sa.UniqueConstraint("tenant_id", "entity_id"),)


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tenants.id"))
    provider: Mapped[str] = mapped_column(sa.Text, default="*")  # '*' = all providers combined
    monthly_cap_usd: Mapped[float] = mapped_column(sa.Numeric(10, 4))
    soft_cap_ratio: Mapped[float] = mapped_column(sa.Numeric(4, 2), default=0.8)

    __table_args__ = (sa.UniqueConstraint("tenant_id", "provider"),)


class HashtagSearchLog(Base):
    """Enforces Instagram's 30-unique-hashtags-per-rolling-7-days quota per account."""

    __tablename__ = "hashtag_search_log"

    id: Mapped[uuid.UUID] = _uuid_pk()
    account_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("accounts.id"))
    hashtag: Mapped[str] = mapped_column(sa.Text)
    searched_at: Mapped[datetime] = _now()

    __table_args__ = (sa.Index("ix_hashtag_search_log_account_time", "account_id", "searched_at"),)


class ContentPlanItem(Base):
    __tablename__ = "content_plan_items"

    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tenants.id"))
    title: Mapped[str] = mapped_column(sa.Text)
    burst_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("bursts.id"))
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("clusters.id"))
    target_platform: Mapped[Platform] = mapped_column(sa.Enum(Platform, native_enum=False))
    planned_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    status: Mapped[PlanStatus] = mapped_column(
        sa.Enum(PlanStatus, native_enum=False), default=PlanStatus.idea
    )
    notes: Mapped[str | None] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = _now()


class Draft(Base):
    __tablename__ = "drafts"

    id: Mapped[uuid.UUID] = _uuid_pk()
    plan_item_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("content_plan_items.id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tenants.id"))
    platform: Mapped[Platform] = mapped_column(sa.Enum(Platform, native_enum=False))
    variant_no: Mapped[int] = mapped_column(sa.Integer, default=1)
    hook: Mapped[str | None] = mapped_column(sa.Text)
    caption: Mapped[str | None] = mapped_column(sa.Text)
    hashtags: Mapped[list | None] = mapped_column(JSONVariant)
    script: Mapped[str | None] = mapped_column(sa.Text)
    media_asset_ids: Mapped[list | None] = mapped_column(JSONVariant)
    llm_model: Mapped[str | None] = mapped_column(sa.Text)
    prompt_version: Mapped[str | None] = mapped_column(sa.Text)
    token_usage: Mapped[dict | None] = mapped_column(JSONVariant)
    status: Mapped[DraftStatus] = mapped_column(
        sa.Enum(DraftStatus, native_enum=False), default=DraftStatus.proposed
    )
    created_at: Mapped[datetime] = _now()
    approved_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[uuid.UUID] = _uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tenants.id"))
    kind: Mapped[str] = mapped_column(sa.Text)  # image|video
    local_path: Mapped[str | None] = mapped_column(sa.Text)
    storage_url: Mapped[str | None] = mapped_column(sa.Text)
    mime: Mapped[str | None] = mapped_column(sa.Text)
    width: Mapped[int | None] = mapped_column(sa.Integer)
    height: Mapped[int | None] = mapped_column(sa.Integer)
    checksum: Mapped[str | None] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = _now()


class Publish(Base):
    __tablename__ = "publishes"

    id: Mapped[uuid.UUID] = _uuid_pk()
    draft_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("drafts.id"))
    platform: Mapped[Platform] = mapped_column(sa.Enum(Platform, native_enum=False))
    method: Mapped[str] = mapped_column(sa.Text)  # ig_graph|tiktok_inbox
    container_id: Mapped[str | None] = mapped_column(sa.Text)
    external_media_id: Mapped[str | None] = mapped_column(sa.Text)
    status: Mapped[PublishStatus] = mapped_column(
        sa.Enum(PublishStatus, native_enum=False), default=PublishStatus.pending
    )
    error: Mapped[str | None] = mapped_column(sa.Text)
    published_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    permalink: Mapped[str | None] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = _now()


# --------------------------------------------------------------------------
# Global dimension tables (shared across tenants — trend data is not per-tenant)
# --------------------------------------------------------------------------


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = _uuid_pk()
    platform: Mapped[Platform] = mapped_column(sa.Enum(Platform, native_enum=False))
    entity_type: Mapped[EntityType] = mapped_column(sa.Enum(EntityType, native_enum=False))
    natural_key: Mapped[str] = mapped_column(sa.Text)  # normalized, e.g. lowercase hashtag
    display_name: Mapped[str | None] = mapped_column(sa.Text)
    meta: Mapped[dict | None] = mapped_column(JSONVariant)
    first_seen: Mapped[datetime] = _now()
    last_seen: Mapped[datetime] = _now()

    __table_args__ = (sa.UniqueConstraint("platform", "entity_type", "natural_key"),)


class ContentItem(Base):
    """First-seen/dedupe dimension for posts. `events` (hypertable) stays append-only;
    uniqueness of a post lives here because hypertable unique indexes must include
    the time column."""

    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = _uuid_pk()
    platform: Mapped[Platform] = mapped_column(sa.Enum(Platform, native_enum=False))
    external_id: Mapped[str] = mapped_column(sa.Text)
    author_external_id: Mapped[str | None] = mapped_column(sa.Text)
    author_handle: Mapped[str | None] = mapped_column(sa.Text)
    first_seen_at: Mapped[datetime] = _now()
    text_hash: Mapped[str | None] = mapped_column(sa.Text)
    minhash_sig: Mapped[bytes | None] = mapped_column(sa.LargeBinary)
    dup_of_content_item_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("content_items.id")
    )

    __table_args__ = (sa.UniqueConstraint("platform", "external_id"),)


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[uuid.UUID] = _uuid_pk()
    label: Mapped[str | None] = mapped_column(sa.Text)
    why_trending: Mapped[str | None] = mapped_column(sa.Text)
    category: Mapped[str | None] = mapped_column(sa.Text)
    centroid = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    status: Mapped[str] = mapped_column(sa.Text, default="active")  # active|stale
    size: Mapped[int] = mapped_column(sa.Integer, default=0)
    sample_content_ids: Mapped[list | None] = mapped_column(JSONVariant)
    prompt_version: Mapped[str | None] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = _now()
    updated_at: Mapped[datetime] = _now()


class ClusterMember(Base):
    __tablename__ = "cluster_members"

    cluster_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("clusters.id"), primary_key=True)
    content_item_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("content_items.id"), primary_key=True
    )
    similarity: Mapped[float | None] = mapped_column(sa.Float)


class Burst(Base):
    __tablename__ = "bursts"

    id: Mapped[uuid.UUID] = _uuid_pk()
    entity_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("entities.id"))
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("clusters.id"))
    state: Mapped[BurstState] = mapped_column(
        sa.Enum(BurstState, native_enum=False), default=BurstState.candidate
    )
    detected_at: Mapped[datetime] = _now()
    burst_start: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    burst_end: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    peak_zscore: Mapped[float | None] = mapped_column(sa.Float)
    peak_bucket: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    kleinberg_level: Mapped[int | None] = mapped_column(sa.Integer)

    __table_args__ = (sa.Index("ix_bursts_entity_state", "entity_id", "state"),)


class EntityBaseline(Base):
    __tablename__ = "entity_baselines"

    entity_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("entities.id"), primary_key=True)
    dow: Mapped[int] = mapped_column(sa.SmallInteger, primary_key=True)  # 0-6
    hour: Mapped[int] = mapped_column(sa.SmallInteger, primary_key=True)  # 0-23
    mean: Mapped[float] = mapped_column(sa.Float)
    std: Mapped[float] = mapped_column(sa.Float)
    sample_weeks: Mapped[int] = mapped_column(sa.Integer, default=0)
    updated_at: Mapped[datetime] = _now()


# --------------------------------------------------------------------------
# Hypertables (TimescaleDB; converted in the initial migration)
# --------------------------------------------------------------------------


class Event(Base):
    """Append-only observation stream. One row per (poll observation of a) post."""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, default=uuid.uuid4, primary_key=True)
    event_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), primary_key=True
    )  # hypertable partition column; part of PK by Timescale requirement
    platform: Mapped[Platform] = mapped_column(sa.Enum(Platform, native_enum=False))
    source_provider: Mapped[str] = mapped_column(sa.Text)
    event_kind: Mapped[str] = mapped_column(sa.Text, default="post")  # post|video|reel|observation
    content_item_id: Mapped[uuid.UUID | None] = mapped_column(sa.Uuid)
    external_id: Mapped[str | None] = mapped_column(sa.Text)
    author_external_id: Mapped[str | None] = mapped_column(sa.Text)
    text: Mapped[str | None] = mapped_column(sa.Text)
    lang: Mapped[str | None] = mapped_column(sa.Text)
    url: Mapped[str | None] = mapped_column(sa.Text)
    metrics: Mapped[dict | None] = mapped_column(JSONVariant)  # views/likes/comments snapshot
    is_first_observation: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(sa.Uuid)  # cost attribution

    __table_args__ = (sa.Index("ix_events_content_item", "content_item_id", "event_time"),)


class EventEntity(Base):
    __tablename__ = "event_entities"

    event_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True)
    event_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), primary_key=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True)
    is_first_observation: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    __table_args__ = (sa.Index("ix_event_entities_entity_time", "entity_id", "event_time"),)


class EntityStats15m(Base):
    __tablename__ = "entity_stats_15m"

    bucket_start: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), primary_key=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True)
    new_mentions: Mapped[int] = mapped_column(sa.Integer, default=0)
    observations: Mapped[int] = mapped_column(sa.Integer, default=0)
    views_sum: Mapped[int] = mapped_column(sa.BigInteger, default=0)
    likes_sum: Mapped[int] = mapped_column(sa.BigInteger, default=0)
    author_count: Mapped[int] = mapped_column(sa.Integer, default=0)


class Embedding(Base):
    __tablename__ = "embeddings"

    content_item_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True)
    embedded_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), primary_key=True, server_default=sa.func.now()
    )
    vector = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    model: Mapped[str] = mapped_column(sa.Text)


class ProviderCall(Base):
    """Cost ledger. Every external call — scraper, official API, LLM, embeddings."""

    __tablename__ = "provider_calls"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, default=uuid.uuid4, primary_key=True)
    call_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), primary_key=True, server_default=sa.func.now()
    )
    provider: Mapped[str] = mapped_column(sa.Text)
    adapter_method: Mapped[str | None] = mapped_column(sa.Text)
    endpoint: Mapped[str | None] = mapped_column(sa.Text)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(sa.Uuid)
    credits_used: Mapped[float | None] = mapped_column(sa.Float)
    est_cost_usd: Mapped[float] = mapped_column(sa.Numeric(10, 6), default=0)
    tokens: Mapped[dict | None] = mapped_column(JSONVariant)
    status_code: Mapped[int | None] = mapped_column(sa.Integer)
    latency_ms: Mapped[int | None] = mapped_column(sa.Integer)
    request_fingerprint: Mapped[str | None] = mapped_column(sa.Text)

    __table_args__ = (sa.Index("ix_provider_calls_provider_time", "provider", "call_time"),)


# Tables safe to create on sqlite for tests (everything except pgvector columns).
SQLITE_SAFE_TABLES = [
    t
    for t in Base.metadata.sorted_tables
    if t.name not in ("clusters", "embeddings")
]

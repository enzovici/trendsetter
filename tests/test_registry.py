import pytest
import sqlalchemy as sa

from trendsetter.db.models import Platform, ProviderCall
from trendsetter.providers.base import (
    Capability,
    FetchRequest,
    ProviderError,
    ProviderResult,
)
from trendsetter.providers.budget import BudgetPolicy
from trendsetter.providers.registry import ProviderRegistry


class FakeAdapter:
    platforms = frozenset({Platform.tiktok})
    capabilities = frozenset({Capability.HASHTAG_POSTS})

    def __init__(self, provider_id: str, fail: bool = False):
        self.provider_id = provider_id
        self.fail = fail

    async def fetch(self, req: FetchRequest) -> ProviderResult:
        if self.fail:
            raise ProviderError(f"{self.provider_id} is down")
        return ProviderResult(provider=self.provider_id, est_cost_usd=0.5)


def make_registry(*adapters: FakeAdapter) -> ProviderRegistry:
    registry = ProviderRegistry.__new__(ProviderRegistry)
    registry._routes = {
        ("tiktok", "hashtag_posts"): [a.provider_id for a in adapters]
    }
    registry._adapters = {a.provider_id: a for a in adapters}
    return registry


REQ = FetchRequest(
    platform=Platform.tiktok,
    capability=Capability.HASHTAG_POSTS,
    params={"hashtag": "fitness"},
)


@pytest.fixture
def flat_policy(monkeypatch):
    monkeypatch.setattr(
        BudgetPolicy, "from_config", classmethod(lambda cls: BudgetPolicy(100.0, 0.8))
    )


async def test_fallback_returns_second_provider_and_records_both(sqlite_session, flat_policy):
    registry = make_registry(FakeAdapter("a", fail=True), FakeAdapter("b"))
    result = await registry.fetch_with_fallback(sqlite_session, REQ)
    assert result.provider == "b"

    calls = (
        (
            await sqlite_session.execute(
                sa.select(ProviderCall).order_by(ProviderCall.provider)
            )
        )
        .scalars()
        .all()
    )
    assert len(calls) == 2
    assert [c.provider for c in calls] == ["a", "b"]
    assert float(calls[0].est_cost_usd) == 0.0
    assert float(calls[1].est_cost_usd) == 0.5


async def test_all_providers_failing_raises(sqlite_session, flat_policy):
    registry = make_registry(FakeAdapter("a", fail=True), FakeAdapter("b", fail=True))
    with pytest.raises(ProviderError):
        await registry.fetch_with_fallback(sqlite_session, REQ)

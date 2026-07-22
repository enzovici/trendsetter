import pytest

from trendsetter.db.models import Platform
from trendsetter.providers.base import (
    Capability,
    FetchRequest,
    ProviderError,
    ProviderResult,
)
from trendsetter.providers.budget import (
    BudgetedClient,
    BudgetExceededError,
    BudgetPolicy,
    BudgetState,
)


class FakeLedger:
    def __init__(self, spend: float = 0.0):
        self.spend = spend
        self.rows: list[dict] = []

    async def month_to_date_usd(self) -> float:
        return self.spend

    async def record(
        self,
        *,
        provider: str,
        adapter_method: str | None,
        endpoint: str | None,
        credits_used: float | None,
        est_cost_usd: float,
        status_code: int | None,
        latency_ms: int | None,
        tokens: dict | None = None,
        tenant_id=None,
    ) -> None:
        self.rows.append(
            {
                "provider": provider,
                "adapter_method": adapter_method,
                "endpoint": endpoint,
                "credits_used": credits_used,
                "est_cost_usd": est_cost_usd,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "tokens": tokens,
                "tenant_id": tenant_id,
            }
        )


class FakeAdapter:
    provider_id = "fake"
    platforms = frozenset({Platform.tiktok})
    capabilities = frozenset({Capability.HASHTAG_POSTS})

    def __init__(self, error: Exception | None = None):
        self.error = error
        self.calls = 0

    async def fetch(self, req: FetchRequest) -> ProviderResult:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return ProviderResult(provider="fake", est_cost_usd=1.0)


REQ = FetchRequest(
    platform=Platform.tiktok,
    capability=Capability.HASHTAG_POSTS,
    params={"hashtag": "fitness"},
)


def make_client(
    spend: float, error: Exception | None = None
) -> tuple[FakeAdapter, FakeLedger, BudgetedClient]:
    adapter = FakeAdapter(error=error)
    ledger = FakeLedger(spend=spend)
    return adapter, ledger, BudgetedClient(adapter, ledger, BudgetPolicy(10.0, 0.8))


async def test_hard_cap_blocks_fetch_before_adapter_call():
    adapter, ledger, client = make_client(spend=10.0)
    with pytest.raises(BudgetExceededError):
        await client.fetch(REQ)
    assert adapter.calls == 0
    assert ledger.rows == []


async def test_soft_cap_reported_but_fetch_allowed():
    adapter, ledger, client = make_client(spend=8.0)
    assert await client.state() is BudgetState.soft_exceeded
    result = await client.fetch(REQ)
    assert result.provider == "fake"
    assert adapter.calls == 1


async def test_successful_fetch_records_ledger_row():
    adapter, ledger, client = make_client(spend=0.0)
    await client.fetch(REQ)
    assert len(ledger.rows) == 1
    row = ledger.rows[0]
    assert row["provider"] == "fake"
    assert row["est_cost_usd"] == 1.0
    assert row["adapter_method"] == "hashtag_posts"
    assert row["endpoint"] == "fitness"


async def test_failed_fetch_still_recorded_and_error_propagates():
    adapter, ledger, client = make_client(spend=0.0, error=ProviderError("upstream 500"))
    with pytest.raises(ProviderError):
        await client.fetch(REQ)
    assert adapter.calls == 1
    assert len(ledger.rows) == 1
    assert ledger.rows[0]["est_cost_usd"] == 0.0

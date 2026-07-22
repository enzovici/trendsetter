"""Budget enforcement: every external call goes through BudgetedClient.

Hard cap -> BudgetExceededError (callers skip gracefully, dashboard shows banner).
Soft cap -> BudgetState.SOFT_EXCEEDED; the scheduler stretches all cadences by the
configured multiplier.
"""

import enum
import time
from datetime import UTC, datetime
from typing import Protocol

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from trendsetter.config import load_yaml
from trendsetter.db.models import ProviderCall
from trendsetter.providers.base import FetchRequest, ProviderAdapter, ProviderResult


class BudgetExceededError(RuntimeError):
    pass


class BudgetState(enum.StrEnum):
    ok = "ok"
    soft_exceeded = "soft_exceeded"
    hard_exceeded = "hard_exceeded"


class Ledger(Protocol):
    async def month_to_date_usd(self) -> float: ...

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
    ) -> None: ...


class DbLedger:
    """Ledger backed by the provider_calls hypertable."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def month_to_date_usd(self) -> float:
        # Month start computed in Python (portable to sqlite in tests).
        month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            sa.select(sa.func.coalesce(sa.func.sum(ProviderCall.est_cost_usd), 0)).where(
                ProviderCall.call_time >= month_start
            )
        )
        return float(result.scalar_one())

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
        self.session.add(
            ProviderCall(
                provider=provider,
                adapter_method=adapter_method,
                endpoint=endpoint,
                credits_used=credits_used,
                est_cost_usd=est_cost_usd,
                status_code=status_code,
                latency_ms=latency_ms,
                tokens=tokens,
                tenant_id=tenant_id,
            )
        )
        await self.session.commit()


class BudgetPolicy:
    def __init__(self, monthly_cap_usd: float, soft_cap_ratio: float):
        self.monthly_cap_usd = monthly_cap_usd
        self.soft_cap_ratio = soft_cap_ratio

    @classmethod
    def from_config(cls) -> "BudgetPolicy":
        cfg = load_yaml("cadence.yml")["budget"]
        return cls(float(cfg["monthly_cap_usd"]), float(cfg["soft_cap_ratio"]))

    def state(self, month_to_date_usd: float) -> BudgetState:
        if month_to_date_usd >= self.monthly_cap_usd:
            return BudgetState.hard_exceeded
        if month_to_date_usd >= self.monthly_cap_usd * self.soft_cap_ratio:
            return BudgetState.soft_exceeded
        return BudgetState.ok


class BudgetedClient:
    def __init__(self, adapter: ProviderAdapter, ledger: Ledger, policy: BudgetPolicy):
        self.adapter = adapter
        self.ledger = ledger
        self.policy = policy

    async def state(self) -> BudgetState:
        return self.policy.state(await self.ledger.month_to_date_usd())

    async def fetch(self, req: FetchRequest, tenant_id=None) -> ProviderResult:
        spend = await self.ledger.month_to_date_usd()
        if self.policy.state(spend) is BudgetState.hard_exceeded:
            raise BudgetExceededError(
                f"monthly budget ${self.policy.monthly_cap_usd:.2f} exhausted "
                f"(spent ${spend:.2f}); skipping {self.adapter.provider_id} call"
            )
        start = time.monotonic()
        result: ProviderResult | None = None
        try:
            result = await self.adapter.fetch(req)
            return result
        finally:
            latency_ms = int((time.monotonic() - start) * 1000)
            # Failed calls are recorded too (cost may still be incurred upstream).
            await self.ledger.record(
                provider=self.adapter.provider_id,
                adapter_method=req.capability.value,
                endpoint=req.params.get("hashtag") or req.params.get("profile_id"),
                credits_used=result.credits_used if result else None,
                est_cost_usd=result.est_cost_usd if result else 0.0,
                status_code=result.meta.get("status_code") if result else None,
                latency_ms=latency_ms,
                tenant_id=tenant_id,
            )

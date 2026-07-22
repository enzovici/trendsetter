"""Resolves (platform, capability) -> ordered adapter list from config/providers.yml
and fetches with fallback: first adapter that succeeds wins; ProviderError and
QuotaExceededError fall through to the next adapter."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from trendsetter.config import load_yaml
from trendsetter.db.models import Platform
from trendsetter.providers.base import (
    Capability,
    FetchRequest,
    ProviderAdapter,
    ProviderError,
    ProviderResult,
)
from trendsetter.providers.budget import BudgetedClient, BudgetPolicy, DbLedger

log = logging.getLogger(__name__)


def _build_adapter(provider_id: str, cfg: dict) -> ProviderAdapter | None:
    if cfg.get("enabled") is False:
        return None
    if provider_id == "scrapecreators":
        from trendsetter.providers.scrapers.scrapecreators import ScrapeCreatorsAdapter

        return ScrapeCreatorsAdapter(
            base_url=cfg["base_url"], cost_per_call_usd=float(cfg.get("cost_per_call_usd", 0))
        )
    if provider_id == "apify":
        from trendsetter.providers.scrapers.apify import ApifyAdapter

        return ApifyAdapter(
            base_url=cfg["base_url"],
            cost_per_item_usd={k: float(v) for k, v in cfg.get("cost_per_item_usd", {}).items()},
        )
    # Official adapters land in M3; unknown/unbuilt ids are skipped, not fatal.
    log.debug("no adapter implementation for provider %r yet", provider_id)
    return None


class ProviderRegistry:
    def __init__(self) -> None:
        cfg = load_yaml("providers.yml")
        self._routes: dict[tuple[str, str], list[str]] = {}
        for platform, caps in (cfg.get("routes") or {}).items():
            for capability, provider_ids in caps.items():
                self._routes[(platform, capability)] = list(provider_ids)
        self._adapters: dict[str, ProviderAdapter] = {}
        for provider_id, provider_cfg in (cfg.get("providers") or {}).items():
            adapter = _build_adapter(provider_id, provider_cfg or {})
            if adapter is not None:
                self._adapters[provider_id] = adapter

    def resolve(self, platform: Platform, capability: Capability) -> list[ProviderAdapter]:
        ids = self._routes.get((platform.value, capability.value), [])
        return [self._adapters[i] for i in ids if i in self._adapters]

    async def fetch_with_fallback(
        self, session: AsyncSession, req: FetchRequest, tenant_id=None
    ) -> ProviderResult:
        adapters = self.resolve(req.platform, req.capability)
        if not adapters:
            raise ProviderError(
                f"no adapter available for ({req.platform.value}, {req.capability.value})"
            )
        policy = BudgetPolicy.from_config()
        ledger = DbLedger(session)
        last_error: Exception | None = None
        for adapter in adapters:
            client = BudgetedClient(adapter, ledger, policy)
            try:
                return await client.fetch(req, tenant_id=tenant_id)
            except ProviderError as exc:  # includes QuotaExceededError
                log.warning("provider %s failed (%s); falling through", adapter.provider_id, exc)
                last_error = exc
        raise ProviderError(
            f"all providers failed for ({req.platform.value}, {req.capability.value})"
        ) from last_error

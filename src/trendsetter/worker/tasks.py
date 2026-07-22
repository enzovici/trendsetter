"""Procrastinate worker app.

Run: procrastinate --app=trendsetter.worker.tasks.app worker
First run needs the procrastinate schema: procrastinate --app=trendsetter.worker.tasks.app schema --apply

M0 periodic jobs: trending pulls for TikTok + Instagram. No API key -> no spend:
each task exits early when SCRAPECREATORS_API_KEY is unset.
"""

import logging

from procrastinate import App, PsycopgConnector

from trendsetter.config import get_settings
from trendsetter.db.models import Platform
from trendsetter.db.session import db_session
from trendsetter.ingest.collectors import pull_trending
from trendsetter.providers.base import Capability, ProviderError
from trendsetter.providers.budget import BudgetExceededError
from trendsetter.providers.registry import ProviderRegistry
from trendsetter.worker.schedules import cadence_cron

log = logging.getLogger(__name__)


def _conninfo() -> str:
    return get_settings().database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


app = App(connector=PsycopgConnector(conninfo=_conninfo()))


async def _run_trending(platform: Platform) -> None:
    if not get_settings().scrapecreators_api_key:
        log.info("SCRAPECREATORS_API_KEY not set; skipping %s trending pull", platform.value)
        return
    registry = ProviderRegistry()
    if not registry.resolve(platform, Capability.TRENDING_FEED):
        log.debug("no trending_feed route configured for %s; skipping", platform.value)
        return
    async with db_session() as session:
        try:
            await pull_trending(session, registry, platform)
        except BudgetExceededError as exc:
            log.warning("budget exhausted, %s trending pull skipped: %s", platform.value, exc)
        except ProviderError as exc:
            log.warning("%s trending pull failed: %s", platform.value, exc)


@app.periodic(cron=cadence_cron("trending_tiktok"))
@app.task(name="trending_tiktok", queueing_lock="trending_tiktok")
async def trending_tiktok(timestamp: int) -> None:
    await _run_trending(Platform.tiktok)


@app.periodic(cron=cadence_cron("trending_instagram"))
@app.task(name="trending_instagram", queueing_lock="trending_instagram")
async def trending_instagram(timestamp: int) -> None:
    await _run_trending(Platform.instagram)

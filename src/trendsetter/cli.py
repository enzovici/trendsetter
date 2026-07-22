"""CLI: manual pulls, seeding, cost summary. `uv run trendsetter --help`"""

import asyncio

import sqlalchemy as sa
import typer

from trendsetter.db.models import Platform, ProviderCall

app = typer.Typer(no_args_is_help=True)


@app.command()
def pull_hashtag(
    platform: Platform,
    hashtag: str,
    limit: int = typer.Option(None, help="posts to fetch (default from cadence.yml)"),
):
    """Pull one hashtag's posts through the provider registry into the DB."""

    async def _run():
        from trendsetter.db.session import db_session
        from trendsetter.ingest.collectors import pull_hashtag as _pull
        from trendsetter.providers.registry import ProviderRegistry

        async with db_session() as session:
            stats = await _pull(session, ProviderRegistry(), platform, hashtag, limit)
            typer.echo(
                f"#{hashtag} ({platform.value}): {stats.events} events, "
                f"{stats.new_content_items} new posts, {len(stats.entities_touched)} entities"
            )

    asyncio.run(_run())


@app.command()
def seed(tenant_name: str = "default"):
    """Create tenant + default budget rows (idempotent)."""

    async def _run():
        from trendsetter.scripts_seed import seed_tenant

        tenant = await seed_tenant(tenant_name)
        typer.echo(f"tenant ready: {tenant.name} ({tenant.id})")

    asyncio.run(_run())


@app.command()
def costs():
    """Month-to-date spend per provider."""

    async def _run():
        from trendsetter.db.session import db_session

        async with db_session() as session:
            month_start = sa.func.date_trunc("month", sa.func.now())
            rows = (
                await session.execute(
                    sa.select(
                        ProviderCall.provider,
                        sa.func.count(),
                        sa.func.coalesce(sa.func.sum(ProviderCall.est_cost_usd), 0),
                    )
                    .where(ProviderCall.call_time >= month_start)
                    .group_by(ProviderCall.provider)
                    .order_by(sa.desc(sa.func.sum(ProviderCall.est_cost_usd)))
                )
            ).all()
            if not rows:
                typer.echo("no calls this month")
                return
            total = 0.0
            for provider, calls, usd in rows:
                typer.echo(f"{provider:20s} {calls:6d} calls  ${float(usd):8.4f}")
                total += float(usd)
            typer.echo(f"{'TOTAL':20s} {'':6s}        ${total:8.4f}")

    asyncio.run(_run())


if __name__ == "__main__":
    app()

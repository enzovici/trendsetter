"""Month-to-date provider spend vs. budget (config/cadence.yml)."""

import calendar
from datetime import UTC, datetime
from pathlib import Path

import sqlalchemy as sa
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from trendsetter.config import load_yaml
from trendsetter.db.models import ProviderCall
from trendsetter.db.session import db_session
from trendsetter.providers.budget import BudgetPolicy

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")


@router.get("/costs", response_class=HTMLResponse)
async def costs(request: Request):
    now = datetime.now(UTC)
    # Month start computed in Python (portable to sqlite in tests), like DbLedger.
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    async with db_session() as session:
        rows = (
            await session.execute(
                sa.select(
                    ProviderCall.provider,
                    sa.func.count().label("calls"),
                    sa.func.coalesce(sa.func.sum(ProviderCall.est_cost_usd), 0).label("usd"),
                )
                .where(ProviderCall.call_time >= month_start)
                .group_by(ProviderCall.provider)
                .order_by(sa.desc("usd"))
            )
        ).all()
    providers = [
        {"provider": provider, "calls": calls, "usd": float(usd)}
        for provider, calls, usd in rows
    ]
    total = sum(p["usd"] for p in providers)

    budget = load_yaml("cadence.yml")["budget"]
    policy = BudgetPolicy(float(budget["monthly_cap_usd"]), float(budget["soft_cap_ratio"]))
    cap = policy.monthly_cap_usd
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    projection = total / now.day * days_in_month

    return templates.TemplateResponse(
        request,
        "costs.html",
        {
            "month": now.strftime("%B %Y"),
            "providers": providers,
            "total": total,
            "cap": cap,
            "soft_cap_usd": cap * policy.soft_cap_ratio,
            "state": policy.state(total).value,
            "spend_pct": min(total / cap * 100, 100) if cap else 0.0,
            "projection": projection,
            "projection_pct": min(projection / cap * 100, 100) if cap else 0.0,
        },
    )

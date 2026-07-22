"""Idempotent seeding: tenant + budget row from cadence.yml defaults."""

import sqlalchemy as sa

from trendsetter.config import load_yaml
from trendsetter.db.models import Budget, Tenant
from trendsetter.db.session import db_session


async def seed_tenant(name: str = "default") -> Tenant:
    async with db_session() as session:
        tenant = (
            await session.execute(sa.select(Tenant).where(Tenant.name == name))
        ).scalar_one_or_none()
        if tenant is None:
            tenant = Tenant(name=name)
            session.add(tenant)
            await session.flush()
        budget = (
            await session.execute(
                sa.select(Budget).where(Budget.tenant_id == tenant.id, Budget.provider == "*")
            )
        ).scalar_one_or_none()
        if budget is None:
            cfg = load_yaml("cadence.yml")["budget"]
            session.add(
                Budget(
                    tenant_id=tenant.id,
                    provider="*",
                    monthly_cap_usd=cfg["monthly_cap_usd"],
                    soft_cap_ratio=cfg["soft_cap_ratio"],
                )
            )
        await session.commit()
        return tenant

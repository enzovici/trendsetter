"""Cadence -> cron translation. All polling intervals live in config/cadence.yml."""

from trendsetter.config import load_yaml


def minutes_to_cron(m: int) -> str:
    if m < 60:
        return f"*/{m} * * * *"
    if m == 60:
        return "0 * * * *"
    if m % 60 == 0:
        return f"0 */{m // 60} * * *"
    raise ValueError(f"cadence of {m} minutes is not expressible as a simple cron rule")


def cadence_cron(job: str) -> str:
    minutes = load_yaml("cadence.yml")["cadence_minutes"][job]
    return minutes_to_cron(int(minutes))

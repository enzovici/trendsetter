"""Record one live provider response into tests/fixtures (spends ~1 credit).

Usage:
    uv run python scripts/record_fixture.py scrapecreators tiktok hashtag_posts fitness
    uv run python scripts/record_fixture.py scrapecreators instagram hashtag_posts fitness

Overwrites the assumed-shape fixture for that (provider, platform, capability).
After recording, run pytest: if the parser drops fields the fixture proves exist,
fix parse_post's key lists in providers/scrapers/scrapecreators.py.
"""

import asyncio
import json
import sys

from trendsetter.config import PROJECT_ROOT
from trendsetter.db.models import Platform
from trendsetter.providers.base import Capability, FetchRequest
from trendsetter.providers.registry import ProviderRegistry


async def main() -> None:
    provider_id, platform, capability, query = sys.argv[1:5]
    registry = ProviderRegistry()
    adapters = [
        a
        for a in registry.resolve(Platform(platform), Capability(capability))
        if a.provider_id == provider_id
    ]
    if not adapters:
        raise SystemExit(f"no adapter {provider_id} for ({platform}, {capability})")
    adapter = adapters[0]

    params = {"limit": 5}
    if capability == Capability.HASHTAG_POSTS:
        params["hashtag"] = query
    elif capability == Capability.PROFILE_POSTS:
        params["profile_id"] = query

    result = await adapter.fetch(
        FetchRequest(platform=Platform(platform), capability=Capability(capability), params=params)
    )
    # Persist raw items (not the parsed RawPosts) so fixtures pin the vendor shape.
    out = {
        "posts": [p.raw for p in result.posts],
        "cursor": result.cursor,
        "credits_used": result.credits_used,
        "_recorded_note": "live response; parsed OK at recording time",
    }
    dest = PROJECT_ROOT / "tests" / "fixtures" / provider_id / f"{platform}_{capability}_{query}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, default=str))
    print(f"recorded {len(result.posts)} posts -> {dest}")
    print(f"est cost: ${result.est_cost_usd:.4f}")


if __name__ == "__main__":
    asyncio.run(main())

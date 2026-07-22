import json
from pathlib import Path

import httpx
import pytest
import respx

from trendsetter.db.models import Platform
from trendsetter.providers.base import Capability, FetchRequest, ProviderError
from trendsetter.providers.scrapers.scrapecreators import ScrapeCreatorsAdapter

FIXTURES = Path(__file__).parent / "fixtures" / "scrapecreators"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def make_adapter(client: httpx.AsyncClient) -> ScrapeCreatorsAdapter:
    return ScrapeCreatorsAdapter(
        base_url="https://api.test", cost_per_call_usd=0.001, client=client
    )


@respx.mock
async def test_tiktok_hashtag_parses_posts():
    respx.get("https://api.test/v1/tiktok/hashtag").mock(
        return_value=httpx.Response(200, json=load_fixture("tiktok_hashtag.json"))
    )
    async with httpx.AsyncClient() as client:
        adapter = make_adapter(client)
        result = await adapter.fetch(
            FetchRequest(
                platform=Platform.tiktok,
                capability=Capability.HASHTAG_POSTS,
                params={"hashtag": "#Fitness", "limit": 10},
            )
        )
    assert len(result.posts) == 3
    post = result.posts[0]
    assert isinstance(post.external_id, str)
    assert "fitness" in post.hashtags
    assert "gym" in post.hashtags
    assert all("fitness" in p.hashtags for p in result.posts)
    assert isinstance(post.metrics["views"], int)
    assert post.sounds
    assert result.est_cost_usd == 0.001
    assert result.cursor == "abc"


@respx.mock
async def test_rate_limited_raises_provider_error():
    respx.get("https://api.test/v1/tiktok/hashtag").mock(return_value=httpx.Response(429))
    async with httpx.AsyncClient() as client:
        adapter = make_adapter(client)
        with pytest.raises(ProviderError):
            await adapter.fetch(
                FetchRequest(
                    platform=Platform.tiktok,
                    capability=Capability.HASHTAG_POSTS,
                    params={"hashtag": "fitness"},
                )
            )


async def test_unsupported_combo_raises_without_http_call():
    def _no_http(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"unexpected HTTP call: {request.url}")

    async with httpx.AsyncClient(transport=httpx.MockTransport(_no_http)) as client:
        adapter = make_adapter(client)
        with pytest.raises(ProviderError):
            await adapter.fetch(
                FetchRequest(platform=Platform.instagram, capability=Capability.TRENDING_FEED)
            )


@respx.mock
async def test_instagram_hashtag_parses():
    respx.get("https://api.test/v1/instagram/hashtag").mock(
        return_value=httpx.Response(200, json=load_fixture("instagram_hashtag.json"))
    )
    async with httpx.AsyncClient() as client:
        adapter = make_adapter(client)
        result = await adapter.fetch(
            FetchRequest(
                platform=Platform.instagram,
                capability=Capability.HASHTAG_POSTS,
                params={"hashtag": "fitness"},
            )
        )
    assert len(result.posts) == 3
    post = result.posts[0]
    assert post.external_id == "3401111111111111111"
    assert post.author_handle == "liftlife.ig"
    assert post.sounds == []
    assert post.metrics["likes"] == 15400
    assert "fitness" in post.hashtags


@respx.mock
async def test_tiktok_trending_returns_entities():
    respx.get("https://api.test/v1/tiktok/trending").mock(
        return_value=httpx.Response(200, json=load_fixture("tiktok_trending.json"))
    )
    async with httpx.AsyncClient() as client:
        adapter = make_adapter(client)
        result = await adapter.fetch(
            FetchRequest(platform=Platform.tiktok, capability=Capability.TRENDING_FEED)
        )
    assert result.posts == []
    assert len(result.entities) == 5
    assert result.entities[0].natural_key == "grwm"
    assert result.entities[0].rank == 1
    assert result.entities[1].natural_key == "fittok"

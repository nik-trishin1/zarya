from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from app.utm import build_redirect_url, merge_utm


def test_merge_utm_request_wins():
    merged = merge_utm(
        {"utm_source": "telegram", "utm_medium": ""},
        {"utm_source": "default", "utm_medium": "qr", "utm_campaign": "spring"},
    )
    assert merged["utm_source"] == "telegram"
    assert merged["utm_medium"] == "qr"
    assert merged["utm_campaign"] == "spring"
    assert merged["utm_content"] is None


def test_build_redirect_url_preserves_and_merges():
    url, utms = build_redirect_url(
        "https://example.com/path?foo=1&utm_source=dest",
        {"utm_medium": "story", "bar": "2"},
        {"utm_source": "default", "utm_campaign": "c1"},
    )
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    assert qs["foo"] == ["1"]
    assert qs["bar"] == ["2"]
    assert qs["utm_source"] == ["dest"]  # already on destination, not blank
    assert qs["utm_medium"] == ["story"]
    assert qs["utm_campaign"] == ["c1"]
    # Logged UTMs: request + defaults only (destination bake-in stays on URL only)
    assert utms["utm_source"] == "default"
    assert utms["utm_medium"] == "story"
    assert utms["utm_campaign"] == "c1"


async def test_create_redirect_stats_flow(client, admin_headers):
    created = await client.post(
        "/links",
        data={
            "destination_url": "https://example.com/event",
            "slug": "demo",
            "utm_source": "poster",
            "utm_medium": "qr",
            "utm_campaign": "april",
        },
        headers=admin_headers,
    )
    assert created.status_code == 200
    assert "http://test/r/demo" in created.text
    assert "/qr/demo.png" in created.text

    # Request overrides source; medium/campaign filled from defaults.
    redirect = await client.get(
        "/r/demo",
        params={"utm_source": "telegram", "ref": "x"},
        follow_redirects=False,
    )
    assert redirect.status_code == 302
    location = redirect.headers["location"]
    qs = parse_qs(urlparse(location).query)
    assert qs["utm_source"] == ["telegram"]
    assert qs["utm_medium"] == ["qr"]
    assert qs["utm_campaign"] == ["april"]
    assert qs["ref"] == ["x"]

    # Second click with full override
    redirect2 = await client.get(
        "/r/demo",
        params={
            "utm_source": "ig",
            "utm_medium": "bio",
            "utm_campaign": "summer",
            "utm_content": "a",
            "utm_term": "b",
        },
        follow_redirects=False,
    )
    assert redirect2.status_code == 302

    stats = await client.get("/stats/demo", headers=admin_headers)
    assert stats.status_code == 200
    assert "Всего кликов: <strong>2</strong>" in stats.text
    assert "telegram" in stats.text
    assert "ig" in stats.text
    assert "qr" in stats.text
    assert "bio" in stats.text


async def test_qr_png(client, admin_headers):
    await client.post(
        "/links",
        data={"destination_url": "https://example.com", "slug": "qr1"},
        headers=admin_headers,
    )
    response = await client.get("/qr/qr1.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


async def test_unknown_slug_404(client):
    assert (await client.get("/r/missing", follow_redirects=False)).status_code == 404
    assert (await client.get("/qr/missing.png")).status_code == 404


async def test_duplicate_slug(client, admin_headers):
    data = {"destination_url": "https://example.com", "slug": "dup"}
    assert (await client.post("/links", data=data, headers=admin_headers)).status_code == 200
    again = await client.post("/links", data=data, headers=admin_headers)
    assert again.status_code == 409

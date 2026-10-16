from __future__ import annotations


async def test_create_unauthorized(client):
    response = await client.post(
        "/links",
        data={"destination_url": "https://example.com"},
    )
    assert response.status_code == 401


async def test_stats_unauthorized(client, admin_headers):
    created = await client.post(
        "/links",
        data={"destination_url": "https://example.com", "slug": "auth-stats"},
        headers=admin_headers,
    )
    assert created.status_code == 200

    # Drop cookie set by create — stats must reject anonymous requests.
    client.cookies.clear()
    response = await client.get("/stats/auth-stats")
    assert response.status_code == 401


async def test_login_sets_cookie(client):
    bad = await client.post("/login", data={"admin_token": "wrong"})
    assert bad.status_code == 401

    ok = await client.post("/login", data={"admin_token": "test-token"}, follow_redirects=False)
    assert ok.status_code == 303
    assert "link_qr_admin" in ok.cookies

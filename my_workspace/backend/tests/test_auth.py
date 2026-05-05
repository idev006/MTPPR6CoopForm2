"""
test_auth.py — Regression tests for Sprint 12 C-01, C-04
Coverage: login success/fail, get_me, refresh token
"""
from httpx import AsyncClient

from app.models.user import User


async def test_login_success(client: AsyncClient, borrower_user: User):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "borrower@test.local",
        "password": "Test1234!",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == "borrower@test.local"
    assert body["user"]["role"] == "borrower"


async def test_login_wrong_password(client: AsyncClient, borrower_user: User):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "borrower@test.local",
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401


async def test_get_me(client: AsyncClient, borrower_user: User, borrower_token: str):
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "borrower@test.local"
    assert body["first_name"] == "สมชาย"


async def test_get_me_no_token(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_refresh_token(client: AsyncClient, borrower_user: User):
    # First login to get refresh cookie
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "borrower@test.local",
        "password": "Test1234!",
    })
    assert login_resp.status_code == 200

    # Refresh using the cookie set by login
    refresh_resp = await client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200
    body = refresh_resp.json()
    assert "access_token" in body

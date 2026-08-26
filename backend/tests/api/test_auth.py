"""Needs postgres running. Make routers/auth.py + queries pass these."""


async def test_signup_returns_a_token(client):
    response = await client.post(
        "/auth/signup", json={"username": "newbie", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["token"]


async def test_signup_rejects_a_taken_username(client):
    body = {"username": "twice", "password": "password123"}
    await client.post("/auth/signup", json=body)
    response = await client.post("/auth/signup", json=body)
    assert response.status_code == 409


async def test_signup_rejects_a_short_password(client):
    response = await client.post(
        "/auth/signup", json={"username": "shorty", "password": "abc"}
    )
    assert response.status_code == 422


async def test_login_works(client):
    await client.post(
        "/auth/signup", json={"username": "loginer", "password": "password123"}
    )
    response = await client.post(
        "/auth/login", json={"username": "loginer", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["token"]


async def test_login_rejects_a_wrong_password(client):
    await client.post(
        "/auth/signup", json={"username": "careful", "password": "password123"}
    )
    response = await client.post(
        "/auth/login", json={"username": "careful", "password": "notthepassword"}
    )
    assert response.status_code == 401


async def test_login_hides_whether_the_user_exists(client):
    """Wrong user and wrong password must look identical from outside."""
    await client.post(
        "/auth/signup", json={"username": "real", "password": "password123"}
    )
    no_user = await client.post(
        "/auth/login", json={"username": "ghost", "password": "password123"}
    )
    bad_password = await client.post(
        "/auth/login", json={"username": "real", "password": "wrongwrong"}
    )
    assert no_user.status_code == bad_password.status_code == 401
    assert no_user.json() == bad_password.json()


async def test_the_password_is_never_stored_raw(client, conn):
    await client.post(
        "/auth/signup", json={"username": "hashed", "password": "password123"}
    )
    row = await (
        await conn.execute(
            "select password_hash from users where username = %s", ("hashed",)
        )
    ).fetchone()
    assert row["password_hash"] != "password123"


async def test_me_needs_a_token(client):
    response = await client.get("/users/me")
    assert response.status_code == 401


async def test_me_rejects_a_made_up_token(client):
    response = await client.get(
        "/users/me", headers={"Authorization": "Bearer notarealtoken"}
    )
    assert response.status_code == 401


async def test_logout_kills_the_token(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    assert (await client.post("/auth/logout", headers=headers)).status_code == 204
    assert (await client.get("/users/me", headers=headers)).status_code == 401

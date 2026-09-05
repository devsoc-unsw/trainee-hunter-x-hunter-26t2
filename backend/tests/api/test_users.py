"""Needs postgres running. Make routers/users.py pass these."""

import keyboard


async def test_me_returns_the_basics(client, auth):
    response = await client.get("/users/me", headers=auth)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "tester"
    assert body["coins"] == 0
    assert body["solved_count"] == 0


async def test_new_user_starts_with_the_starting_keys(client, auth):
    body = (await client.get("/users/me", headers=auth)).json()
    # unlocked_keys is WHICH keys now, not how many - the user picks each one
    assert body["unlocked_keys"] == sorted(keyboard.STARTING_KEY_CHARS)
    # and nothing left over to place, since the starting keys are already spent
    assert body["unlock_credits"] == 0


async def test_me_never_leaks_the_password_hash(client, auth):
    body = (await client.get("/users/me", headers=auth)).json()
    assert "password_hash" not in body
    assert "password" not in body


async def test_can_change_username(client, auth):
    response = await client.patch(
        "/users/me", json={"username": "renamed"}, headers=auth
    )
    assert response.status_code == 200
    assert response.json()["username"] == "renamed"


async def test_cannot_take_someone_elses_username(client, auth):
    await client.post(
        "/auth/signup", json={"username": "taken", "password": "password123"}
    )
    response = await client.patch("/users/me", json={"username": "taken"}, headers=auth)
    assert response.status_code == 409


async def test_empty_patch_changes_nothing(client, auth):
    response = await client.patch("/users/me", json={}, headers=auth)
    assert response.status_code == 200
    assert response.json()["username"] == "tester"

"""Needs postgres running. Covers routers/decor.py, mounted at /keyboard.

Two rules this file exists to pin down:

  * an item dresses as many keys as you BOUGHT copies of it, and taking it off
    a key makes it placeable again;
  * which key a new unlock lands on is the user's choice, not the next slot in
    a fixed order.
"""

import pytest

import keyboard

LOCKED_KEY = "z"  # not in STARTING_KEY_CHARS


@pytest.fixture
async def rich(conn, auth):
    """Gives the test user 1000 coins so they can actually buy things."""
    await conn.execute("update users set coins = 1000 where username = %s", ("tester",))
    return auth


@pytest.fixture
async def shop(client, auth) -> dict:
    items = (await client.get("/shop", headers=auth)).json()
    return {item["slug"]: item for item in items}


async def buy(client, headers, shop: dict, slug: str, times: int = 1) -> None:
    for _ in range(times):
        response = await client.post(f"/shop/{shop[slug]['id']}/buy", headers=headers)
        assert response.status_code == 200, response.text


# ---------- unlocking a key ----------


async def test_a_new_keyboard_is_the_home_row(client, auth):
    body = (await client.get("/users/me", headers=auth)).json()
    assert body["unlocked_keys"] == sorted(keyboard.STARTING_KEY_CHARS)
    assert LOCKED_KEY not in body["unlocked_keys"]


async def test_cannot_unlock_without_a_credit(client, auth):
    response = await client.post(f"/keyboard/{LOCKED_KEY}/unlock", headers=auth)
    assert response.status_code == 409
    body = (await client.get("/users/me", headers=auth)).json()
    assert LOCKED_KEY not in body["unlocked_keys"]


async def test_buying_a_key_lets_you_choose_where_it_goes(client, rich, shop):
    await buy(client, rich, shop, "extra-key")
    assert (await client.get("/users/me", headers=rich)).json()["unlock_credits"] == 1

    response = await client.post(f"/keyboard/{LOCKED_KEY}/unlock", headers=rich)
    assert response.status_code == 200
    body = response.json()
    assert body["key_char"] == LOCKED_KEY
    assert LOCKED_KEY in body["unlocked_keys"]
    assert body["unlock_credits"] == 0

    # the credit is spent - a second key needs a second purchase
    assert (await client.post("/keyboard/x/unlock", headers=rich)).status_code == 409


async def test_cannot_unlock_the_same_key_twice(client, rich, shop):
    await buy(client, rich, shop, "extra-key")
    await client.post(f"/keyboard/{LOCKED_KEY}/unlock", headers=rich)

    response = await client.post(f"/keyboard/{LOCKED_KEY}/unlock", headers=rich)
    assert response.status_code == 409
    # and the credit must not have been eaten by the failed attempt
    assert (await client.get("/users/me", headers=rich)).json()["unlock_credits"] == 0


async def test_unlocking_a_key_that_is_not_on_the_board(client, rich, shop):
    await buy(client, rich, shop, "extra-key")
    assert (await client.post("/keyboard/[/unlock", headers=rich)).status_code == 422
    assert (await client.post("/keyboard/ab/unlock", headers=rich)).status_code == 422
    # the credit survives a rejected key
    assert (await client.get("/users/me", headers=rich)).json()["unlock_credits"] == 1


async def test_unlock_needs_a_login(client):
    assert (await client.post(f"/keyboard/{LOCKED_KEY}/unlock")).status_code == 401


# ---------- placing items, limited by quantity ----------


async def test_cannot_decorate_a_locked_key(client, rich, shop):
    await buy(client, rich, shop, "blue-tulip")
    response = await client.put(
        f"/keyboard/{LOCKED_KEY}/accessory",
        json={"accessory_slug": "blue-tulip"},
        headers=rich,
    )
    assert response.status_code == 403


async def test_cannot_place_what_you_do_not_own(client, auth):
    response = await client.put(
        "/keyboard/f/accessory", json={"accessory_slug": "blue-tulip"}, headers=auth
    )
    assert response.status_code == 403


async def test_one_copy_dresses_one_key(client, rich, shop):
    await buy(client, rich, shop, "blue-tulip")

    first = await client.put(
        "/keyboard/f/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )
    assert first.status_code == 200
    assert first.json()["accessory_slug"] == "blue-tulip"

    # they own one, and it's already on f
    second = await client.put(
        "/keyboard/j/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )
    assert second.status_code == 409


async def test_buying_two_dresses_two_keys(client, rich, shop):
    await buy(client, rich, shop, "blue-tulip", times=2)

    for key in ("f", "j"):
        response = await client.put(
            f"/keyboard/{key}/accessory",
            json={"accessory_slug": "blue-tulip"},
            headers=rich,
        )
        assert response.status_code == 200

    third = await client.put(
        "/keyboard/d/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )
    assert third.status_code == 409


async def test_replacing_the_same_item_on_a_key_is_allowed(client, rich, shop):
    """A key must not compete with itself for its own last copy."""
    await buy(client, rich, shop, "blue-tulip")
    await client.put(
        "/keyboard/f/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )
    again = await client.put(
        "/keyboard/f/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )
    assert again.status_code == 200


async def test_removing_an_item_frees_it_to_replant(client, rich, shop):
    await buy(client, rich, shop, "blue-tulip")
    await client.put(
        "/keyboard/f/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )

    # take it off f, and the same copy goes on j - no repurchase
    await client.put("/keyboard/f/accessory", json={"accessory_slug": None}, headers=rich)
    moved = await client.put(
        "/keyboard/j/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )
    assert moved.status_code == 200

    inventory = (await client.get("/shop/inventory", headers=rich)).json()
    tulip = next(i for i in inventory if i["slug"] == "blue-tulip")
    assert (tulip["quantity"], tulip["placed"]) == (1, 1)


async def test_clearing_a_key_returns_both_slots(client, rich, shop):
    await buy(client, rich, shop, "soil-key")
    await buy(client, rich, shop, "blue-tulip")
    await client.put("/keyboard/f/skin", json={"skin_slug": "soil-key"}, headers=rich)
    await client.put(
        "/keyboard/f/accessory", json={"accessory_slug": "blue-tulip"}, headers=rich
    )

    assert (await client.delete("/keyboard/f", headers=rich)).status_code == 204

    inventory = {i["slug"]: i for i in (await client.get("/shop/inventory", headers=rich)).json()}
    assert inventory["soil-key"]["placed"] == 0
    assert inventory["blue-tulip"]["placed"] == 0


async def test_skins_are_limited_by_quantity_too(client, rich, shop):
    await buy(client, rich, shop, "soil-key")
    assert (
        await client.put("/keyboard/f/skin", json={"skin_slug": "soil-key"}, headers=rich)
    ).status_code == 200
    assert (
        await client.put("/keyboard/j/skin", json={"skin_slug": "soil-key"}, headers=rich)
    ).status_code == 409


async def test_evicted_accessory_becomes_placeable_again(client, rich, shop):
    """A fish knocked off a key by a skin change is free to place elsewhere."""
    await buy(client, rich, shop, "water-key", times=2)
    await buy(client, rich, shop, "soil-key")
    await buy(client, rich, shop, "fish")

    await client.put("/keyboard/f/skin", json={"skin_slug": "water-key"}, headers=rich)
    await client.put("/keyboard/j/skin", json={"skin_slug": "water-key"}, headers=rich)
    await client.put("/keyboard/f/accessory", json={"accessory_slug": "fish"}, headers=rich)

    # f stops being water, so the fish is evicted by set_skin
    await client.put("/keyboard/f/skin", json={"skin_slug": "soil-key"}, headers=rich)

    moved = await client.put(
        "/keyboard/j/accessory", json={"accessory_slug": "fish"}, headers=rich
    )
    assert moved.status_code == 200


async def test_habitat_rule_still_applies(client, rich, shop):
    await buy(client, rich, shop, "fish")
    # f has no skin, so it's the default grass key - land
    response = await client.put(
        "/keyboard/f/accessory", json={"accessory_slug": "fish"}, headers=rich
    )
    assert response.status_code == 409

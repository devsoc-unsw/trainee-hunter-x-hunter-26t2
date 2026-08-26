"""Needs postgres running. Make routers/shop.py pass these."""

import pytest


@pytest.fixture
async def rich(conn, auth, client):
    """Gives the test user 1000 coins so they can actually buy things."""
    await conn.execute("update users set coins = 1000 where username = %s", ("tester",))
    return auth


@pytest.fixture
async def cheapest_item(client, auth) -> dict:
    items = (await client.get("/shop", headers=auth)).json()
    return min(items, key=lambda item: item["price"])


async def test_shop_needs_a_login(client):
    assert (await client.get("/shop")).status_code == 401


async def test_shop_lists_items(client, auth):
    response = await client.get("/shop", headers=auth)
    assert response.status_code == 200
    assert len(response.json()) >= 4
    assert all("price" in item for item in response.json())


async def test_new_user_owns_nothing(client, auth):
    assert (await client.get("/shop/inventory", headers=auth)).json() == []
    assert all(item["owned"] is False for item in (await client.get("/shop", headers=auth)).json())


async def test_buying_deducts_coins(client, rich, cheapest_item):
    response = await client.post(f"/shop/{cheapest_item['id']}/buy", headers=rich)
    assert response.status_code == 200
    assert response.json()["coins_left"] == 1000 - cheapest_item["price"]


async def test_buying_puts_it_in_your_inventory(client, rich, cheapest_item):
    await client.post(f"/shop/{cheapest_item['id']}/buy", headers=rich)
    inventory = (await client.get("/shop/inventory", headers=rich)).json()
    assert [item["id"] for item in inventory] == [cheapest_item["id"]]


async def test_owned_items_are_marked_in_the_shop(client, rich, cheapest_item):
    await client.post(f"/shop/{cheapest_item['id']}/buy", headers=rich)
    items = (await client.get("/shop", headers=rich)).json()
    assert next(i for i in items if i["id"] == cheapest_item["id"])["owned"] is True


async def test_cannot_buy_twice(client, rich, cheapest_item):
    await client.post(f"/shop/{cheapest_item['id']}/buy", headers=rich)
    coins = (await client.get("/users/me", headers=rich)).json()["coins"]

    response = await client.post(f"/shop/{cheapest_item['id']}/buy", headers=rich)
    assert response.status_code == 409
    # and it must not have charged them again
    assert (await client.get("/users/me", headers=rich)).json()["coins"] == coins


async def test_cannot_buy_what_you_cannot_afford(client, auth, cheapest_item):
    # this user has 0 coins
    response = await client.post(f"/shop/{cheapest_item['id']}/buy", headers=auth)
    assert response.status_code == 402
    assert (await client.get("/users/me", headers=auth)).json()["coins"] == 0
    assert (await client.get("/shop/inventory", headers=auth)).json() == []


async def test_buying_something_that_does_not_exist_is_404(client, rich):
    response = await client.post(
        "/shop/00000000-0000-0000-0000-000000000000/buy", headers=rich
    )
    assert response.status_code == 404


async def test_coins_never_go_negative(client, rich, conn):
    """Buy everything until it stops working, balance must stay >= 0."""
    items = (await client.get("/shop", headers=rich)).json()
    for item in items:
        await client.post(f"/shop/{item['id']}/buy", headers=rich)
    assert (await client.get("/users/me", headers=rich)).json()["coins"] >= 0

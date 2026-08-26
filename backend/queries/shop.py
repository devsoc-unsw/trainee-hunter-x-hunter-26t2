from uuid import UUID

import psycopg


async def list_items(conn: psycopg.AsyncConnection) -> list[dict]:
    # everything for sale, cheapest first
    raise NotImplementedError


async def get_item(conn: psycopg.AsyncConnection, item_id: UUID) -> dict | None:
    raise NotImplementedError


async def list_inventory(conn: psycopg.AsyncConnection, user_id: UUID) -> list[dict]:
    # the items this user owns. join inventory -> shop_items
    raise NotImplementedError


async def owns_item(
    conn: psycopg.AsyncConnection, user_id: UUID, item_id: UUID
) -> bool:
    raise NotImplementedError


async def add_to_inventory(
    conn: psycopg.AsyncConnection, user_id: UUID, item_id: UUID
) -> bool:
    # give the item to the user. False if they already had it
    raise NotImplementedError

from uuid import UUID

import psycopg
from psycopg.rows import DictRow


async def list_items(conn: psycopg.AsyncConnection[DictRow]) -> list[dict]:
    # everything for sale, cheapest first
    return await (
        await conn.execute("select * from shop_items order by price, name")
    ).fetchall()


async def get_item(conn: psycopg.AsyncConnection[DictRow], item_id: UUID) -> dict | None:
    return await (
        await conn.execute("select * from shop_items where id = %s", (item_id,))
    ).fetchone()


async def list_inventory(conn: psycopg.AsyncConnection[DictRow], user_id: UUID) -> list[dict]:
    # the items this user owns. join inventory -> shop_items
    return await (
        await conn.execute(
            """
            select shop_items.*
            from inventory
            join shop_items on shop_items.id = inventory.item_id
            where inventory.user_id = %s
            """,
            (user_id,),
        )
    ).fetchall()


async def owns_item(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, item_id: UUID
) -> bool:
    row = await (
        await conn.execute(
            "select 1 from inventory where user_id = %s and item_id = %s",
            (user_id, item_id),
        )
    ).fetchone()
    return row is not None


async def add_to_inventory(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, item_id: UUID
) -> bool:
    # give the item to the user. False if they already had it
    row = await (
        await conn.execute(
            """
            insert into inventory (user_id, item_id)
            values (%s, %s)
            on conflict (user_id, item_id) do nothing
            returning user_id
            """,
            (user_id, item_id),
        )
    ).fetchone()
    return row is not None

async def get_item_by_slug(
    conn: psycopg.AsyncConnection[DictRow], slug: str
) -> dict | None:
    return await (
        await conn.execute("select * from shop_items where slug = %s", (slug,))
    ).fetchone()
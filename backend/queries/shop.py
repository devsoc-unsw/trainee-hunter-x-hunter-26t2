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
    # the items this user owns, with how many they bought and how many are
    # currently sitting on a key. join inventory -> shop_items.
    #
    # `placed` is counted off key_decor rather than stored in a column on
    # purpose: two numbers that must agree can drift, one number and a select
    # can't. it's also why nothing in this codebase has to 'refund' an item -
    # taking it off a key makes it available again by definition.
    return await (
        await conn.execute(
            """
            select shop_items.*,
                   inventory.quantity,
                   (select count(*)
                      from key_decor
                     where key_decor.user_id = inventory.user_id
                       and (key_decor.skin_id = inventory.item_id
                            or key_decor.accessory_id = inventory.item_id)) as placed
            from inventory
            join shop_items on shop_items.id = inventory.item_id
            where inventory.user_id = %s
            order by shop_items.price, shop_items.name
            """,
            (user_id,),
        )
    ).fetchall()


async def owns_item(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, item_id: UUID
) -> bool:
    # has the user ever bought this? deliberately NOT 'do they have a spare
    # one' - see units_available. the two are different answers: 'you don't own
    # that' is a 403, 'you've planted them all' is a 409.
    row = await (
        await conn.execute(
            "select 1 from inventory where user_id = %s and item_id = %s",
            (user_id, item_id),
        )
    ).fetchone()
    return row is not None


async def add_to_inventory(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, item_id: UUID
) -> int:
    # give the user one more of the item, return how many they now own.
    # buying the same thing again stacks instead of failing - the primary key
    # used to BE the buy-once rule, now it's just what keeps one row per item
    # so key_decor's composite foreign key has something to point at.
    row = await (
        await conn.execute(
            """
            insert into inventory (user_id, item_id, quantity)
            values (%s, %s, 1)
            on conflict (user_id, item_id)
            do update set quantity = inventory.quantity + 1
            returning quantity
            """,
            (user_id, item_id),
        )
    ).fetchone()
    assert row is not None  # insert-or-update always returns the row
    return row["quantity"]


async def units_available(
    conn: psycopg.AsyncConnection[DictRow],
    user_id: UUID,
    item_id: UUID,
    *,
    ignoring_key: str | None = None,
) -> int:
    # how many copies of this item are free to put on a key: bought minus
    # placed. 0 if they don't own it at all.
    #
    # `for update` locks this user's inventory row for the rest of the
    # request's transaction. without it two placements arriving together both
    # read placed = 0, both see the last copy as free, and both write - the
    # count subquery alone can't stop that because they touch different
    # key_decor rows, so there's nothing for postgres to serialise on. with it
    # the second request waits for the first to commit and then reads placed=1.
    #
    # ignoring_key excludes one key from the count, so re-placing the item a
    # key is ALREADY wearing doesn't have to compete with itself.
    row = await (
        await conn.execute(
            """
            select quantity from inventory
            where user_id = %s and item_id = %s
            for update
            """,
            (user_id, item_id),
        )
    ).fetchone()
    if row is None:
        return 0

    placed = await (
        await conn.execute(
            """
            select count(*) as n from key_decor
            where user_id = %s
              and (skin_id = %s or accessory_id = %s)
              and key_char is distinct from %s
            """,
            (user_id, item_id, item_id, ignoring_key),
        )
    ).fetchone()
    assert placed is not None  # count(*) always returns exactly one row
    return row["quantity"] - placed["n"]

async def get_item_by_slug(
    conn: psycopg.AsyncConnection[DictRow], slug: str
) -> dict | None:
    return await (
        await conn.execute("select * from shop_items where slug = %s", (slug,))
    ).fetchone()
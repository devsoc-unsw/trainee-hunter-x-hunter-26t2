from uuid import UUID

import psycopg
from psycopg.rows import DictRow


async def list_key_decor(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID
) -> list[dict]:
    # how every decorated key on this user's keyboard is dressed. keys they
    # haven't touched have no row at all - the frontend draws those as the
    # default grass key with nothing on it.
    #
    # joins out to the slugs because that's what the frontend keys its images
    # off; the raw uuids are no use to it.
    return await (
        await conn.execute(
            """
            select key_decor.key_char,
                   skin.slug      as skin_slug,
                   accessory.slug as accessory_slug
            from key_decor
            left join shop_items as skin      on skin.id      = key_decor.skin_id
            left join shop_items as accessory on accessory.id = key_decor.accessory_id
            where key_decor.user_id = %s
            order by key_decor.key_char
            """,
            (user_id,),
        )
    ).fetchall()


async def set_skin(
    conn: psycopg.AsyncConnection[DictRow],
    user_id: UUID,
    key_char: str,
    skin_id: UUID | None,
    keep_accessory: bool,
) -> dict:
    # recolour one key. skin_id None puts it back to the default grass.
    #
    # keep_accessory closes a hole no constraint can: change a water key to
    # soil and its fish is suddenly sitting on dry land. the route has already
    # read the skin item to check ownership, so it knows both habitats and
    # passes a plain bool - no cross-table subquery needed, and the fish is
    # cleared in the same statement that moves the key.
    #
    # raises ForeignKeyViolation if they don't own the skin. that check is the
    # composite foreign key doing its job, not something to re-implement here.
    row = await (
        await conn.execute(
            """
            insert into key_decor (user_id, key_char, skin_id, accessory_id)
            values (%s, %s, %s, null)
            on conflict (user_id, key_char) do update
            set skin_id      = excluded.skin_id,
                accessory_id = case when %s then key_decor.accessory_id else null end,
                updated_at   = now()
            returning key_char, skin_id, accessory_id
            """,
            (user_id, key_char, skin_id, keep_accessory),
        )
    ).fetchone()
    assert row is not None  # insert-or-update always returns the row
    return row


async def set_accessory(
    conn: psycopg.AsyncConnection[DictRow],
    user_id: UUID,
    key_char: str,
    accessory_id: UUID | None,
) -> dict:
    # put one accessory on a key, replacing whatever was there. accessory_id
    # None takes it off. the primary key on (user_id, key_char) is what makes
    # this a replace instead of a second flower piling up on the same key.
    #
    # raises ForeignKeyViolation if they don't own it - see set_skin.
    row = await (
        await conn.execute(
            """
            insert into key_decor (user_id, key_char, accessory_id)
            values (%s, %s, %s)
            on conflict (user_id, key_char) do update
            set accessory_id = excluded.accessory_id,
                updated_at   = now()
            returning key_char, skin_id, accessory_id
            """,
            (user_id, key_char, accessory_id),
        )
    ).fetchone()
    assert row is not None  # insert-or-update always returns the row
    return row


async def clear_key(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, key_char: str
) -> bool:
    # strip a key back to the default. False if it was never decorated.
    row = await (
        await conn.execute(
            """
            delete from key_decor
            where user_id = %s and key_char = %s
            returning key_char
            """,
            (user_id, key_char),
        )
    ).fetchone()
    return row is not None

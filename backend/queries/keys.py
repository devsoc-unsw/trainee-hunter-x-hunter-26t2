"""Which keys a user has unlocked.

keyboard.py works out how many unlocks they've EARNED; this is where the ones
they've SPENT live. Credits left is the subtraction, done in the route.
"""

from collections.abc import Sequence
from uuid import UUID

import psycopg
from psycopg.rows import DictRow


async def list_unlocked(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID
) -> list[str]:
    # every key char this user has unlocked. the frontend draws exactly these
    # as real keys and everything else as wood.
    rows = await (
        await conn.execute(
            "select key_char from key_unlocks where user_id = %s order by key_char",
            (user_id,),
        )
    ).fetchall()
    return [row["key_char"] for row in rows]


async def count_unlocked(conn: psycopg.AsyncConnection[DictRow], user_id: UUID) -> int:
    row = await (
        await conn.execute(
            "select count(*) as n from key_unlocks where user_id = %s", (user_id,)
        )
    ).fetchone()
    assert row is not None  # count(*) always returns exactly one row
    return row["n"]


async def grant_keys(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, key_chars: Sequence[str]
) -> None:
    # unlock these keys outright, no credit spent. only used for the keys every
    # account starts with. 'on conflict do nothing' makes it safe to re-run.
    if not key_chars:
        return
    await conn.execute(
        """
        insert into key_unlocks (user_id, key_char)
        select %s, unnest(%s::text[])
        on conflict (user_id, key_char) do nothing
        """,
        (user_id, list(key_chars)),
    )


async def unlock_key(
    conn: psycopg.AsyncConnection[DictRow],
    user_id: UUID,
    key_char: str,
    allowance: int,
) -> bool:
    # spend one unlock credit on this key. True if it unlocked.
    #
    # the guard is in the WHERE clause, the same shape as spend_coins: the
    # count of keys already unlocked has to be under the allowance for the
    # insert to produce a row at all, so two requests landing at once can't
    # both spend the last credit. no row back means either they were out of
    # credits or the key was already unlocked - the route reads which, since
    # they're different answers to the user.
    row = await (
        await conn.execute(
            """
            insert into key_unlocks (user_id, key_char)
            select %s, %s
            where (select count(*) from key_unlocks where user_id = %s) < %s
            on conflict (user_id, key_char) do nothing
            returning key_char
            """,
            (user_id, key_char, user_id, allowance),
        )
    ).fetchone()
    return row is not None


async def is_unlocked(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, key_char: str
) -> bool:
    row = await (
        await conn.execute(
            "select 1 from key_unlocks where user_id = %s and key_char = %s",
            (user_id, key_char),
        )
    ).fetchone()
    return row is not None

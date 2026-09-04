from uuid import UUID

import psycopg
from psycopg.rows import DictRow


async def record_press(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, key_char: str
) -> int:
    # count one press, return the new running total for that key.
    #
    # the upsert does insert-or-increment in one statement, so two presses
    # arriving at once can't both read 5 and both write 6. `returning` hands
    # back the new total in the same round trip, which is what a payout rule
    # like "a coin every 10 presses" needs - no extra column, no second read.
    row = await (
        await conn.execute(
            """
            insert into key_presses (user_id, key_char, presses)
            values (%s, %s, 1)
            on conflict (user_id, key_char)
            do update set presses = key_presses.presses + 1
            returning presses
            """,
            (user_id, key_char),
        )
    ).fetchone()
    assert row is not None  # the upsert either inserts or updates, never neither
    return row["presses"]


async def list_presses(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID
) -> dict[str, int]:
    # every key this user has pressed, shaped for the Keyboard component's
    # pressCounts prop. keys never pressed are simply absent.
    rows = await (
        await conn.execute(
            "select key_char, presses from key_presses where user_id = %s",
            (user_id,),
        )
    ).fetchall()
    return {row["key_char"]: row["presses"] for row in rows}


async def total_presses(conn: psycopg.AsyncConnection[DictRow], user_id: UUID) -> int:
    row = await (
        await conn.execute(
            "select coalesce(sum(presses), 0) as n from key_presses where user_id = %s",
            (user_id,),
        )
    ).fetchone()
    assert row is not None  # an aggregate with no group by always returns one row
    return row["n"]

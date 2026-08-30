from uuid import UUID

import psycopg
from psycopg.rows import DictRow


async def mark_solved(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, question_id: UUID
) -> bool:
    # record a solve. returns True if this is the FIRST time (so the route
    # knows whether to pay out). look up 'on conflict do nothing' - it makes
    # this one query instead of a check-then-insert race
    row = await (
        await conn.execute(
            """
            insert into completions (user_id, question_id)
            values (%s, %s)
            on conflict (user_id, question_id) do nothing
            returning question_id
            """,
            (user_id, question_id),
        )
    ).fetchone()
    return row is not None


async def has_solved(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, question_id: UUID
) -> bool:
    row = await (
        await conn.execute(
            "select 1 from completions where user_id = %s and question_id = %s",
            (user_id, question_id),
        )
    ).fetchone()
    return row is not None


async def list_solved_ids(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID
) -> set[UUID]:
    # every question id this user has solved. a set so the questions route
    # can check membership cheaply
    rows = await (
        await conn.execute(
            "select question_id from completions where user_id = %s", (user_id,)
        )
    ).fetchall()
    return {row["question_id"] for row in rows}


async def count_solved(conn: psycopg.AsyncConnection[DictRow], user_id: UUID) -> int:
    # how many solved, drives the keyboard size
    row = await (
        await conn.execute(
            "select count(*) as n from completions where user_id = %s", (user_id,)
        )
    ).fetchone()
    assert row is not None  # count(*) always returns exactly one row
    return row["n"]

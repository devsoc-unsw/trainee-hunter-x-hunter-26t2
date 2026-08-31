from uuid import UUID

import psycopg
from psycopg.rows import DictRow

from models import User


async def create_user(
    conn: psycopg.AsyncConnection[DictRow], username: str, password_hash: str
) -> User:
    # insert a new user, return it. raises psycopg.errors.UniqueViolation if
    # the username is taken - let it raise, the route handles it
    row = await (
        await conn.execute(
            """
            insert into users (username, password_hash)
            values (%s, %s)
            returning id, username, coins
            """,
            (username, password_hash),
        )
    ).fetchone()
    assert row is not None  # insert either returns a row or raises
    return User(**row)


async def get_user_by_username(
    conn: psycopg.AsyncConnection[DictRow], username: str
) -> dict | None:
    # the whole row including password_hash, for login. None if no such user
    return await (
        await conn.execute("select * from users where username = %s", (username,))
    ).fetchone()


async def get_user_by_id(conn: psycopg.AsyncConnection[DictRow], user_id: UUID) -> User | None:
    # None if no such user
    row = await (
        await conn.execute(
            "select id, username, coins from users where id = %s", (user_id,)
        )
    ).fetchone()
    return User(**row) if row else None


async def set_username(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, username: str
) -> None:
    await conn.execute(
        "update users set username = %s where id = %s", (username, user_id)
    )


async def add_coins(conn: psycopg.AsyncConnection[DictRow], user_id: UUID, amount: int) -> int:
    # add coins, return the new balance
    row = await (
        await conn.execute(
            "update users set coins = coins + %s where id = %s returning coins",
            (amount, user_id),
        )
    ).fetchone()
    assert row is not None  # id must belong to an existing user
    return row["coins"]


async def spend_coins(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, amount: int
) -> int | None:
    # take coins off, return the new balance.
    # must NOT let the balance go negative - do the check in the where clause
    # (coins >= %s) and return None if no row was updated, otherwise two
    # requests at the same time can both pass a python-side check
    row = await (
        await conn.execute(
            """
            update users set coins = coins - %s
            where id = %s and coins >= %s
            returning coins
            """,
            (amount, user_id, amount),
        )
    ).fetchone()
    return row["coins"] if row else None

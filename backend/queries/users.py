from uuid import UUID

import psycopg

from models import User


async def create_user(
    conn: psycopg.AsyncConnection, username: str, password_hash: str
) -> User:
    # insert a new user, return it. raises psycopg.errors.UniqueViolation if
    # the username is taken - let it raise, the route handles it
    raise NotImplementedError


async def get_user_by_username(
    conn: psycopg.AsyncConnection, username: str
) -> dict | None:
    # the whole row including password_hash, for login. None if no such user
    raise NotImplementedError


async def get_user_by_id(conn: psycopg.AsyncConnection, user_id: UUID) -> User | None:
    # None if no such user
    raise NotImplementedError


async def set_username(
    conn: psycopg.AsyncConnection, user_id: UUID, username: str
) -> None:
    raise NotImplementedError


async def add_coins(conn: psycopg.AsyncConnection, user_id: UUID, amount: int) -> int:
    # add coins, return the new balance
    raise NotImplementedError


async def spend_coins(
    conn: psycopg.AsyncConnection, user_id: UUID, amount: int
) -> int | None:
    # take coins off, return the new balance.
    # must NOT let the balance go negative - do the check in the where clause
    # (coins >= %s) and return None if no row was updated, otherwise two
    # requests at the same time can both pass a python-side check
    raise NotImplementedError

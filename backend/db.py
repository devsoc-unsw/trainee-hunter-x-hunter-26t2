"""Database connection. This one is done for you."""

import os
from collections.abc import AsyncIterator

import psycopg
from psycopg.rows import DictRow, dict_row


def database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://app:app@localhost:5432/trainee_hunter",
    )


async def get_conn() -> AsyncIterator[psycopg.AsyncConnection[DictRow]]:
    """FastAPI dependency. Opens a connection, commits, closes.

    Use it in a route like:

        @router.get("/thing")
        async def thing(conn: Conn):
            ...

    rows come back as dicts, so row["username"] not row[0].
    """
    async with await psycopg.AsyncConnection[DictRow].connect(
        database_url(), row_factory=dict_row
    ) as connection:
        yield connection

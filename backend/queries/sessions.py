from uuid import UUID

import psycopg
from psycopg.rows import DictRow

from models import User


async def create_session(
    conn: psycopg.AsyncConnection[DictRow], user_id: UUID, token: str
) -> None:
    await conn.execute(
        "insert into sessions (token, user_id) values (%s, %s)",
        (token, user_id),
    )


async def get_user_for_token(conn: psycopg.AsyncConnection[DictRow], token: str) -> User | None:
    # join sessions -> users. None if the token is unknown
    row = await (
        await conn.execute(
            """
            select users.id, users.username, users.coins, users.keys_bought
            from sessions
            join users on users.id = sessions.user_id
            where sessions.token = %s
            """,
            (token,),
        )
    ).fetchone()
    return User(**row) if row else None


async def delete_session(conn: psycopg.AsyncConnection[DictRow], token: str) -> None:
    # logout. deleting a token that doesn't exist is fine, not an error
    await conn.execute("delete from sessions where token = %s", (token,))

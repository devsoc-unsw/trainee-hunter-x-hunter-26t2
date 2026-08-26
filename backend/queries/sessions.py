from uuid import UUID

import psycopg

from models import User


async def create_session(
    conn: psycopg.AsyncConnection, user_id: UUID, token: str
) -> None:
    raise NotImplementedError


async def get_user_for_token(conn: psycopg.AsyncConnection, token: str) -> User | None:
    # join sessions -> users. None if the token is unknown
    raise NotImplementedError


async def delete_session(conn: psycopg.AsyncConnection, token: str) -> None:
    # logout. deleting a token that doesn't exist is fine, not an error
    raise NotImplementedError

"""Shared dependencies. This one is done for you.

`Conn` and `CurrentUser` are the two things routes annotate their arguments
with. FastAPI sees the annotation and fills the argument in.
"""

from typing import Annotated

import psycopg
from fastapi import Depends, Header, HTTPException

import queries.sessions
from db import get_conn
from models import User

Conn = Annotated[psycopg.AsyncConnection, Depends(get_conn)]


async def current_user(
    conn: Conn,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """Turns the Authorization header into a User, or 401s.

    Frontend sends `Authorization: Bearer <token>`.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not logged in")

    token = authorization.removeprefix("Bearer ").strip()
    user = await queries.sessions.get_user_for_token(conn, token)
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    return user


CurrentUser = Annotated[User, Depends(current_user)]

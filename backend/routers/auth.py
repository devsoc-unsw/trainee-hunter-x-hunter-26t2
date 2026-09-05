from typing import Annotated

import psycopg
from fastapi import APIRouter, Header, HTTPException

import queries.sessions
import queries.users
import security
from deps import Conn, CurrentUser
from models import LoginRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(body: SignupRequest, conn: Conn):
    password_hash = security.hash_password(body.password)

    try:
        user = await queries.users.create_user(conn, body.username, password_hash)
    except psycopg.errors.UniqueViolation:
        await conn.rollback()
        raise HTTPException(status_code=409, detail="Username already taken")

    token = security.new_session_token()
    await queries.sessions.create_session(conn, user.id, token)
    return TokenResponse(token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, conn: Conn):
    # wrong username and wrong password must give the SAME 401 - reuse one
    # exception instance for both so the response body is byte-identical
    invalid_credentials = HTTPException(
        status_code=401, detail="Invalid username or password"
    )

    user_row = await queries.users.get_user_by_username(conn, body.username)
    if user_row is None:
        raise invalid_credentials

    if not security.verify_password(body.password, user_row["password_hash"]):
        raise invalid_credentials

    token = security.new_session_token()
    await queries.sessions.create_session(conn, user_row["id"], token)
    return TokenResponse(token=token)


@router.post("/logout", status_code=204)
async def logout(
    conn: Conn,
    user: CurrentUser,
    authorization: Annotated[str | None, Header()] = None,
):
    assert authorization is not None  # CurrentUser already validated this
    token = authorization.removeprefix("Bearer ").strip()
    await queries.sessions.delete_session(conn, token)

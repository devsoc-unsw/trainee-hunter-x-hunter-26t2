from typing import Annotated

from fastapi import APIRouter, Header

from deps import Conn, CurrentUser
from models import LoginRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(body: SignupRequest, conn: Conn):
    # hash the password, create the user, make a session, return the token.
    # username already taken -> 409. catch UniqueViolation, don't check first
    raise NotImplementedError


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, conn: Conn):
    # look up the user, verify the password, make a session, return the token.
    # wrong username and wrong password must give the SAME 401 message,
    # otherwise you're telling people which usernames exist
    raise NotImplementedError


@router.post("/logout", status_code=204)
async def logout(
    conn: Conn,
    user: CurrentUser,
    authorization: Annotated[str | None, Header()] = None,
):
    # delete this session token. returns nothing
    raise NotImplementedError

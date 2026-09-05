from fastapi import APIRouter, HTTPException, status
import psycopg

from deps import Conn, CurrentUser
from models import Me, UpdateMeRequest
from keyboard import unlock_allowance
from queries.keys import list_unlocked
from queries.users import count_solved, set_username

router = APIRouter(prefix="/users", tags=["users"])


async def _me(conn, user, username: str, solved_count: int) -> Me:
    # the keyboard half of /users/me, built once for both routes below.
    #
    # two different numbers, and they're both needed: unlocked_keys is what the
    # frontend draws, unlock_credits is how many more keys the user may click.
    # keyboard.py knows how many unlocks were EARNED, key_unlocks knows which
    # were SPENT, and the difference is what's left.
    unlocked = await list_unlocked(conn, user.id)
    allowance = unlock_allowance(solved_count, user.keys_bought)
    return Me(
        id=user.id,
        username=username,
        coins=user.coins,
        solved_count=solved_count,
        unlocked_keys=unlocked,
        unlock_credits=max(0, allowance - len(unlocked)),
    )


@router.get("/me", response_model=Me)
async def get_me(conn: Conn, user: CurrentUser):
    # username, coins, solved count, which keys are unlocked and how many
    # unlocks are still going spare
    solved_count = await count_solved(conn, user.id)
    return await _me(conn, user, user.username, solved_count)


@router.patch("/me", response_model=Me)
async def update_me(body: UpdateMeRequest, conn: Conn, user: CurrentUser):
    # change username. taken -> 409. body with nothing set = no change, still 200
    if body.username is not None:
        try:
            await set_username(conn, user.id, body.username)
        except psycopg.errors.UniqueViolation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

    solved_count = await count_solved(conn, user.id)
    updated_username = body.username if body.username is not None else user.username
    return await _me(conn, user, updated_username, solved_count)

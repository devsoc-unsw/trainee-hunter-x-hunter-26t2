from fastapi import APIRouter, HTTPException, status
import psycopg

from deps import Conn, CurrentUser
from models import Me, UpdateMeRequest
from keyboard import unlocked_key_count
from queries.users import count_solved, set_username

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=Me)
async def get_me(conn: Conn, user: CurrentUser):
    # username, coins, solved count, and how many keys are unlocked.
    # keyboard.unlocked_key_count() does the last bit
    solved_count = await count_solved(conn, user.id)
    return Me(
        id=user.id,
        username=user.username,
        coins=user.coins,
        solved_count=solved_count,
        unlocked_keys=unlocked_key_count(solved_count),
    )


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
    return Me(
        id=user.id,
        username=updated_username,
        coins=user.coins,
        solved_count=solved_count,
        unlocked_keys=unlocked_key_count(solved_count),
    )

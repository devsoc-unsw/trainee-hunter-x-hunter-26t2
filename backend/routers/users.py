from fastapi import APIRouter

from deps import Conn, CurrentUser
from models import Me, UpdateMeRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=Me)
async def get_me(conn: Conn, user: CurrentUser):
    # username, coins, solved count, and how many keys are unlocked.
    # keyboard.unlocked_key_count() does the last bit
    raise NotImplementedError


@router.patch("/me", response_model=Me)
async def update_me(body: UpdateMeRequest, conn: Conn, user: CurrentUser):
    # change username. taken -> 409. body with nothing set = no change, still 200
    raise NotImplementedError

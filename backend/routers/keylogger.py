from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from deps import Conn, CurrentUser
from queries.keypresses import record_press
from queries.keys import is_unlocked
from queries.users import add_coins

router = APIRouter(prefix="/keylogger", tags=["keylogger"])

PRESSES_PER_COIN = 10


class KeyPayload(BaseModel):
    key: str


class LogKeyResponse(BaseModel):
    key: str
    count: int
    coins_earned: int


@router.post("/log-key", response_model=LogKeyResponse)
async def log_key(payload: KeyPayload, conn: Conn, user: CurrentUser):
    key = payload.key.lower()

    if len(key) != 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid key"
        )

    # which keys are unlocked is a set the user chose, not a count - so this
    # asks the table rather than recomputing a prefix of the unlock order
    if not await is_unlocked(conn, user.id, key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Key is locked"
        )

    new_total = await record_press(conn, user.id, key)

    coins_earned = 0
    if new_total % PRESSES_PER_COIN == 0:
        coins_earned = 1
        await add_coins(conn, user.id, coins_earned)

    return LogKeyResponse(key=key, count=new_total, coins_earned=coins_earned)

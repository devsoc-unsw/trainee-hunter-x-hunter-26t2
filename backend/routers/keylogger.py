from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from deps import Conn, CurrentUser
from keyboard import unlocked_keys
from queries.keypresses import record_press
from queries.progress import count_solved
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
async def log_key(payload: KeyPayload, conn:Conn, user:CurrentUser):
    key = payload.key.lower()

    if len(key) != 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid key"
        )
    solved_count = await count_solved(conn, user.id)
    if key not in unlocked_keys(solved_count):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Key is locked"
        )

    new_total = await record_press(conn, user.id, key)

    coins_earned = 0;

    if new_total % PRESSES_PER_COIN == 0:
        coins_earned = 1
        await add_coins(conn, user.id, coins_earned)
        # print(f"[KEYLOGGER] Pressed: '{key}' | Total count: {key_counts[key]}")
    
    # # Increment press count
    # key_counts[key] = key_counts.get(key, 0) + 1

    # Print log statement to terminal
    return LogKeyResponse(key=key, count=new_total, coins_earned=coins_earned)

    # return {
    #     "status": "success",
    #     "key": key,
    #     "count": key_counts[key],
    # }
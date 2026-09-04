from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/keylogger", tags=["keylogger"])

# In-memory store for quick testing
key_counts: dict[str, int] = {}


class KeyPayload(BaseModel):
    key: str


@router.post("/log-key")
async def log_key(payload: KeyPayload):
    key = payload.key.lower()

    # Increment press count
    key_counts[key] = key_counts.get(key, 0) + 1

    # Print log statement to terminal
    print(f"[KEYLOGGER] Pressed: '{key}' | Total count: {key_counts[key]}")

    return {
        "status": "success",
        "key": key,
        "count": key_counts[key],
    }
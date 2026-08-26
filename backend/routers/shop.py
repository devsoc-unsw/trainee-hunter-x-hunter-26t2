from uuid import UUID

from fastapi import APIRouter

from deps import Conn, CurrentUser
from models import BuyResponse, ShopItem

router = APIRouter(prefix="/shop", tags=["shop"])


@router.get("", response_model=list[ShopItem])
async def list_shop(conn: Conn, user: CurrentUser):
    # everything for sale, with owned=True for stuff the user already has
    raise NotImplementedError


@router.get("/inventory", response_model=list[ShopItem])
async def get_inventory(conn: Conn, user: CurrentUser):
    # just the owned ones. owned is always True here
    raise NotImplementedError


@router.post("/{item_id}/buy", response_model=BuyResponse)
async def buy(item_id: UUID, conn: Conn, user: CurrentUser):
    # 404 if no such item, 409 if already owned, 402 if they can't afford it.
    # spend the coins FIRST - if spend_coins comes back None they were too
    # poor, so bail before adding to inventory
    raise NotImplementedError

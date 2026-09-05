from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from deps import Conn, CurrentUser
from models import BuyResponse, ShopItem
from keyboard import MAX_BUYABLE_KEYS
from queries.shop import add_to_inventory, get_item, list_inventory, list_items, owns_item
from queries.users import buy_key_unlock, spend_coins

router = APIRouter(prefix="/shop", tags=["shop"])


@router.get("", response_model=list[ShopItem])
async def list_shop(conn: Conn, user: CurrentUser):
    # everything for sale, with owned=True for stuff the user already has
    items = await list_items(conn)
    owned_ids = {row["id"] for row in await list_inventory(conn, user.id)}
    return [
        ShopItem(**item, owned=item["id"] in owned_ids)
        for item in items
    ]


@router.get("/inventory", response_model=list[ShopItem])
async def get_inventory(conn: Conn, user: CurrentUser):
    # just the owned ones. owned is always True here
    items = await list_inventory(conn, user.id)
    return [ShopItem(**item, owned=True) for item in items]


@router.post("/{item_id}/buy", response_model=BuyResponse)
async def buy(item_id: UUID, conn: Conn, user: CurrentUser):
    # 404 if no such item, 409 if already owned, 402 if they can't afford it.
    # spend the coins FIRST - if spend_coins comes back None they were too
    # poor, so bail before adding to inventory
    item = await get_item(conn, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if item["kind"] == "key_unlock":
        result = await buy_key_unlock(conn, user.id, item["price"], MAX_BUYABLE_KEYS)
        if result is None:
            if user.keys_bought >= MAX_BUYABLE_KEYS:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="All keys already unlocked",
                )
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Not enough coins",
            )
        return BuyResponse(item_id=item_id, coins_left=result["coins"])
    
    if await owns_item(conn, user.id, item_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already owned")

    new_balance = await spend_coins(conn, user.id, item["price"])
    if new_balance is None:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Not enough coins",
        )

    await add_to_inventory(conn, user.id, item_id)

    return BuyResponse(item_id=item_id, coins_left=new_balance)

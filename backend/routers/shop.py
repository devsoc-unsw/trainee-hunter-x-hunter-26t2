from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from deps import Conn, CurrentUser
from models import BuyResponse, ShopItem
from keyboard import KEY_UNLOCK_ORDER, MAX_BUYABLE_KEYS, unlock_allowance
from queries.shop import add_to_inventory, get_item, list_inventory, list_items
from queries.users import buy_key_unlock, count_solved, spend_coins

router = APIRouter(prefix="/shop", tags=["shop"])


def _to_shop_item(item: dict, quantity: int, placed: int) -> ShopItem:
    return ShopItem(
        **{k: v for k, v in item.items() if k not in ("quantity", "placed")},
        owned=quantity > 0,
        quantity=quantity,
        placed=placed,
    )


@router.get("", response_model=list[ShopItem])
async def list_shop(conn: Conn, user: CurrentUser):
    # everything for sale, with how many of each the user owns and how many of
    # those are already on a key. nothing is buy-once any more, so `owned` is
    # a badge rather than a gate - the buy button stays live at any quantity.
    items = await list_items(conn)
    held = {row["id"]: row for row in await list_inventory(conn, user.id)}
    return [
        _to_shop_item(
            item,
            held[item["id"]]["quantity"] if item["id"] in held else 0,
            held[item["id"]]["placed"] if item["id"] in held else 0,
        )
        for item in items
    ]


@router.get("/inventory", response_model=list[ShopItem])
async def get_inventory(conn: Conn, user: CurrentUser):
    # just the owned ones, with their counts. a row can sit at quantity 0 -
    # nothing deletes inventory rows, because key_decor's foreign key cascades
    # off them - so this is not the same as "owns at least one".
    return [
        _to_shop_item(row, row["quantity"], row["placed"])
        for row in await list_inventory(conn, user.id)
    ]


@router.post("/{item_id}/buy", response_model=BuyResponse)
async def buy(item_id: UUID, conn: Conn, user: CurrentUser):
    # 404 if no such item, 402 if they can't afford it. buying the same thing
    # again is fine now - it stacks. spend the coins FIRST: if spend_coins
    # comes back None they were too poor, so bail before touching inventory
    item = await get_item(conn, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if item["kind"] == "key_unlock":
        # a key unlock isn't an inventory item - it's a credit, banked on
        # users.keys_bought and spent later by clicking a locked key. refuse
        # the sale if the whole board is already accounted for, so coins can't
        # be burned on a credit that has nowhere to go.
        solved_count = await count_solved(conn, user.id)
        if unlock_allowance(solved_count, user.keys_bought) >= len(KEY_UNLOCK_ORDER):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Every key is already unlocked or paid for",
            )

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
        return BuyResponse(item_id=item_id, coins_left=result["coins"], quantity=0)

    new_balance = await spend_coins(conn, user.id, item["price"])
    if new_balance is None:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Not enough coins",
        )

    quantity = await add_to_inventory(conn, user.id, item_id)

    return BuyResponse(item_id=item_id, coins_left=new_balance, quantity=quantity)

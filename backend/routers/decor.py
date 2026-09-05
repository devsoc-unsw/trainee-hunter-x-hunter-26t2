from fastapi import APIRouter, HTTPException, status

from deps import Conn, CurrentUser
from models import KeyDecor, SetAccessoryRequest, SetSkinRequest
from queries.decor import clear_key, list_key_decor, set_accessory, set_skin
from queries.shop import get_item_by_slug, owns_item

router = APIRouter(prefix="/keyboard", tags=["keyboard"])


async def _row_to_decor(row: dict) -> KeyDecor:
    return KeyDecor(
        key_char=row["key_char"],
        skin_slug=row.get("skin_slug"),
        accessory_slug=row.get("accessory_slug"),
    )


@router.get("/decor", response_model=list[KeyDecor])
async def get_decor(conn: Conn, user: CurrentUser):
    rows = await list_key_decor(conn, user.id)
    return [KeyDecor(**row) for row in rows]
@router.put("/{key_char}/skin", response_model=KeyDecor)
async def put_skin(key_char: str, body: SetSkinRequest, conn: Conn, user: CurrentUser):
    if len(key_char) != 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid key")

    skin_id = None
    if body.skin_slug is not None:
        item = await get_item_by_slug(conn, body.skin_slug)
        if item is None or item["kind"] != "key_skin":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skin not found")
        if not await owns_item(conn, user.id, item["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't own that skin")
        skin_id = item["id"]

    row = await set_skin(conn, user.id, key_char, skin_id, body.keep_accessory)

    # set_skin returns raw ids, not slugs - re-fetch this key's decor to get
    # the slug-shaped row list_key_decor already knows how to build
    decor = await list_key_decor(conn, user.id)
    updated = next(d for d in decor if d["key_char"] == key_char)
    return await _row_to_decor(updated)

@router.put("/{key_char}/accessory", response_model=KeyDecor)
async def put_accessory(key_char: str, body: SetAccessoryRequest, conn: Conn, user: CurrentUser):
    if len(key_char) != 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid key")

    accessory_id = None
    if body.accessory_slug is not None:
        item = await get_item_by_slug(conn, body.accessory_slug)
        if item is None or item["kind"] != "accessory":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accessory not found")
        if not await owns_item(conn, user.id, item["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't own that accessory")

        # habitat rule: an accessory can only go on a key of the same habitat.
        # a key with no skin yet is the default grass key, treated as 'land'.
        current = next(
            (d for d in await list_key_decor(conn, user.id) if d["key_char"] == key_char),
            None,
        )
        current_habitat = "land"
        if current and current["skin_slug"] is not None:
            skin_item = await get_item_by_slug(conn, current["skin_slug"])
            current_habitat = skin_item["habitat"]

        if item["habitat"] != current_habitat:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That accessory doesn't match this key's habitat",
            )

        accessory_id = item["id"]

    await set_accessory(conn, user.id, key_char, accessory_id)

    decor = await list_key_decor(conn, user.id)
    updated = next(d for d in decor if d["key_char"] == key_char)
    return await _row_to_decor(updated)


@router.delete("/{key_char}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_decor(key_char: str, conn: Conn, user: CurrentUser):
    if len(key_char) != 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid key")
    await clear_key(conn, user.id, key_char)
    return None
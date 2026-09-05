from fastapi import APIRouter, HTTPException, status

from deps import Conn, CurrentUser
from keyboard import is_real_key, unlock_allowance
from models import KeyDecor, SetAccessoryRequest, SetSkinRequest, UnlockResponse
from queries.decor import clear_key, list_key_decor, set_accessory, set_skin
from queries.keys import is_unlocked, list_unlocked, unlock_key
from queries.shop import get_item_by_slug, owns_item, units_available
from queries.users import count_solved

router = APIRouter(prefix="/keyboard", tags=["keyboard"])


async def _row_to_decor(row: dict) -> KeyDecor:
    return KeyDecor(
        key_char=row["key_char"],
        skin_slug=row.get("skin_slug"),
        accessory_slug=row.get("accessory_slug"),
    )


def _validate_key(key_char: str) -> str:
    # returns the normalised char. key_decor and key_unlocks both store
    # lowercase, so 'F' and 'f' have to mean the same key or a user could
    # unlock one and decorate the other.
    key_char = key_char.lower()
    if len(key_char) != 1 or not is_real_key(key_char):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid key"
        )
    return key_char


async def _require_unlocked(conn, user_id, key_char: str) -> None:
    # key_decor's foreign key into key_unlocks would reject this anyway, but as
    # a 500 rather than an answer. check it here so the user gets told.
    if not await is_unlocked(conn, user_id, key_char):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Key is locked"
        )


async def _require_a_spare(conn, user_id, item: dict, key_char: str) -> None:
    # 'you own one' and 'you have one going spare' are different questions now.
    # ignoring_key excludes the key we're about to write, so re-placing an item
    # a key already wears doesn't count as competing with itself.
    spare = await units_available(conn, user_id, item["id"], ignoring_key=key_char)
    if spare < 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"All your {item['name']} are already on other keys",
        )


async def _decor_for(conn, user_id, key_char: str) -> KeyDecor:
    # set_skin/set_accessory return raw ids, not slugs - re-fetch this key's
    # decor to get the slug-shaped row list_key_decor already knows how to build
    decor = await list_key_decor(conn, user_id)
    updated = next(d for d in decor if d["key_char"] == key_char)
    return await _row_to_decor(updated)


@router.get("/decor", response_model=list[KeyDecor])
async def get_decor(conn: Conn, user: CurrentUser):
    rows = await list_key_decor(conn, user.id)
    return [KeyDecor(**row) for row in rows]


@router.post("/{key_char}/unlock", response_model=UnlockResponse)
async def unlock(key_char: str, conn: Conn, user: CurrentUser):
    # spend one unlock credit on this key. which key is the user's choice -
    # that's the whole point of this route - so the only rules are that it's a
    # real key, it isn't already unlocked, and they have a credit to spend.
    key_char = _validate_key(key_char)

    if await is_unlocked(conn, user.id, key_char):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Key already unlocked"
        )

    solved_count = await count_solved(conn, user.id)
    allowance = unlock_allowance(solved_count, user.keys_bought)

    if not await unlock_key(conn, user.id, key_char, allowance):
        # the insert's WHERE clause said no, and we already ruled out 'already
        # unlocked' above, so they're out of credits
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No unlocks left - solve a problem or buy one",
        )

    unlocked = await list_unlocked(conn, user.id)
    return UnlockResponse(
        key_char=key_char,
        unlocked_keys=unlocked,
        unlock_credits=max(0, allowance - len(unlocked)),
    )


@router.put("/{key_char}/skin", response_model=KeyDecor)
async def put_skin(key_char: str, body: SetSkinRequest, conn: Conn, user: CurrentUser):
    key_char = _validate_key(key_char)
    await _require_unlocked(conn, user.id, key_char)

    skin_id = None
    if body.skin_slug is not None:
        item = await get_item_by_slug(conn, body.skin_slug)
        if item is None or item["kind"] != "key_skin":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skin not found")
        if not await owns_item(conn, user.id, item["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't own that skin")
        await _require_a_spare(conn, user.id, item, key_char)
        skin_id = item["id"]

    # the skin this key was wearing (if any) needs no refund - it stops being
    # counted as placed the moment this row stops pointing at it.
    await set_skin(conn, user.id, key_char, skin_id, body.keep_accessory)

    return await _decor_for(conn, user.id, key_char)


@router.put("/{key_char}/accessory", response_model=KeyDecor)
async def put_accessory(key_char: str, body: SetAccessoryRequest, conn: Conn, user: CurrentUser):
    key_char = _validate_key(key_char)
    await _require_unlocked(conn, user.id, key_char)

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

        await _require_a_spare(conn, user.id, item, key_char)
        accessory_id = item["id"]

    await set_accessory(conn, user.id, key_char, accessory_id)

    return await _decor_for(conn, user.id, key_char)


@router.delete("/{key_char}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_decor(key_char: str, conn: Conn, user: CurrentUser):
    # strip the key back to bare grass. both items go back to being placeable
    # elsewhere with no refund step - 'placed' is counted off this table, so
    # deleting the row IS the refund.
    key_char = _validate_key(key_char)
    await clear_key(conn, user.id, key_char)
    return None

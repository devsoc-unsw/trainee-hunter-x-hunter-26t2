"""What can be placed on what.

Fish and jellyfish belong on water keys, flowers and vegetables on everything
else. That rule can't live in the database: a check constraint can only see
the row it's on, and the accessory's habitat and the skin's habitat are two
rows in shop_items. A trigger could reach across, but nothing else in this
codebase uses triggers, so it lives here instead - pure functions, no
database, unit-testable, exactly like keyboard.py owns the unlock order.
"""

# what a key with no skin renders as. not a shop item: going back to the
# default is free, so there's nothing to buy and nothing to store.
DEFAULT_SKIN = "grass"

# every skin, and which habitat it counts as. shop_items.habitat holds the
# same value for the two that are actually sold; grass is only here because
# it's the default nobody buys.
SKIN_HABITATS = {
    "grass": "land",
    "soil": "land",
    "water": "water",
}


def can_place(accessory_habitat: str, skin_habitat: str) -> bool:
    """Can an accessory of this habitat sit on a key of that habitat?"""
    return accessory_habitat == skin_habitat

"""The keyboard grows as you solve problems - but you choose where.

Solving a problem and buying an 'extra-key' both earn an unlock *credit*.
Spending one is a separate choice: the user clicks any locked key on the
profile page and that key unlocks. So this module owns two halves of the rule
and the database owns the third:

    unlock_allowance()  - how many keys you have EARNED  (pure, here)
    key_unlocks table   - which keys you SPENT them on   (queries/keys.py)
    credits = allowance - count(key_unlocks)             (routers/users.py)

There is deliberately no `unlocked_keys()` function any more. It used to
return KEY_UNLOCK_ORDER[:count], which is only correct while unlocking is a
fixed prefix - it isn't, so the answer has to come from the table.
"""

# every key on the board. no longer the order they unlock in - the user picks
# that - but the front of it is still what a new account starts with, and
# membership is what makes a key char valid at all.
KEY_UNLOCK_ORDER = [
    "f", "j", "d", "k", "s", "l", "a", ";",
    "g", "h", "r", "u", "e", "i", "w", "o", "q", "p",
    "t", "y", "v", "m", "c", "n", "x", "b", "z", ",", ".", "/",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
]

# solves needed per extra key
SOLVES_PER_KEY = 1

# you start with this many, so the keyboard isn't empty on signup
STARTING_KEYS = 4

# the keys every new account gets for free. granted by queries.users.create_user
# rather than chosen, so a fresh keyboard is home row rather than empty.
STARTING_KEY_CHARS = KEY_UNLOCK_ORDER[:STARTING_KEYS]

MAX_BUYABLE_KEYS = len(KEY_UNLOCK_ORDER) - STARTING_KEYS


def unlock_allowance(solved_count: int, keys_bought: int = 0) -> int:
    # how many keys the user is ENTITLED to have unlocked. starts at
    # STARTING_KEYS, grows with solves and with keys bought, caps at the size
    # of the board. what they've actually spent it on lives in key_unlocks -
    # the difference is how many credits they still have to place.
    count = STARTING_KEYS + (solved_count // SOLVES_PER_KEY) + keys_bought
    return min(count, len(KEY_UNLOCK_ORDER))


def is_real_key(key_char: str) -> bool:
    # a key char you could actually unlock. the length check in the schema is
    # only a sanity guard - this is the real list, and python owns it.
    return key_char in KEY_UNLOCK_ORDER

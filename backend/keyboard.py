"""The keyboard grows as you solve problems.

The backend decides how many keys are unlocked, the frontend just draws
that many. Keeps the two in sync and makes this easy to unit test.
"""

# keys unlock in this order. index 0 is unlocked from the start.
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


def unlocked_key_count(solved_count: int) -> int:
    # how many keys are unlocked. starts at STARTING_KEYS, grows with solves,
    # caps at len(KEY_UNLOCK_ORDER)
    count = STARTING_KEYS + (solved_count // SOLVES_PER_KEY)
    return min(count, len(KEY_UNLOCK_ORDER))


def unlocked_keys(solved_count: int) -> list[str]:
    # the actual key characters that are unlocked
    return KEY_UNLOCK_ORDER[:unlocked_key_count(solved_count)]

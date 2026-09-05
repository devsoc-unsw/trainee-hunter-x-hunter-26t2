"""How many coins a solve is worth."""

COINS_BY_DIFFICULTY = {
    "easy": 10,
    "medium": 25,
    "hard": 50,
}


def coins_for_solve(difficulty: str) -> int:
    # coins for solving a question of this difficulty. 0 if difficulty is junk.
    #
    # .get with a default rather than [] on purpose: an unknown difficulty is
    # a data problem, not a reason to 500 a submission the user just spent
    # five minutes on. they get graded, they just don't get paid.
    return COINS_BY_DIFFICULTY.get(difficulty.strip().lower(), 0)

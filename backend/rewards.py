"""How many coins a solve is worth."""

COINS_BY_DIFFICULTY = {
    "easy": 10,
    "medium": 25,
    "hard": 50,
}


def coins_for_solve(difficulty: str) -> int:
    # coins for solving a question of this difficulty. 0 if difficulty is junk
    raise NotImplementedError

"""No database needed. Make rewards.py pass these."""

import rewards


def test_harder_pays_more():
    easy = rewards.coins_for_solve("easy")
    medium = rewards.coins_for_solve("medium")
    hard = rewards.coins_for_solve("hard")
    assert easy < medium < hard


def test_always_pays_something():
    for difficulty in ("easy", "medium", "hard"):
        assert rewards.coins_for_solve(difficulty) > 0


def test_unknown_difficulty_pays_nothing():
    assert rewards.coins_for_solve("impossible") == 0

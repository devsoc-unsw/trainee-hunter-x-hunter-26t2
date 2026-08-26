"""No database needed. Make keyboard.py pass these."""

import keyboard


def test_new_user_gets_starting_keys():
    assert keyboard.unlocked_key_count(0) == keyboard.STARTING_KEYS


def test_solving_unlocks_more():
    assert keyboard.unlocked_key_count(3) > keyboard.unlocked_key_count(0)


def test_never_goes_backwards():
    counts = [keyboard.unlocked_key_count(n) for n in range(50)]
    assert counts == sorted(counts)


def test_caps_at_the_full_keyboard():
    assert keyboard.unlocked_key_count(99999) == len(keyboard.KEY_UNLOCK_ORDER)


def test_unlocked_keys_matches_the_count():
    for solved in (0, 5, 20, 500):
        assert len(keyboard.unlocked_keys(solved)) == keyboard.unlocked_key_count(solved)


def test_unlocked_keys_come_from_the_front_of_the_order():
    keys = keyboard.unlocked_keys(2)
    assert keys == keyboard.KEY_UNLOCK_ORDER[: len(keys)]

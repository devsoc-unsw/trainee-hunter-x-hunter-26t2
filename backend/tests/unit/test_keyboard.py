"""No database needed. Make keyboard.py pass these."""

import keyboard


def test_new_user_gets_starting_keys():
    assert keyboard.unlock_allowance(0) == keyboard.STARTING_KEYS


def test_solving_unlocks_more():
    assert keyboard.unlock_allowance(3) > keyboard.unlock_allowance(0)


def test_buying_unlocks_more():
    assert keyboard.unlock_allowance(0, keys_bought=2) == keyboard.STARTING_KEYS + 2


def test_never_goes_backwards():
    counts = [keyboard.unlock_allowance(n) for n in range(50)]
    assert counts == sorted(counts)


def test_caps_at_the_full_keyboard():
    assert keyboard.unlock_allowance(99999) == len(keyboard.KEY_UNLOCK_ORDER)


def test_starting_keys_are_real_keys():
    assert len(keyboard.STARTING_KEY_CHARS) == keyboard.STARTING_KEYS
    assert all(keyboard.is_real_key(key) for key in keyboard.STARTING_KEY_CHARS)


def test_is_real_key_rejects_anything_not_on_the_board():
    assert keyboard.is_real_key("f")
    assert not keyboard.is_real_key("F")  # callers lowercase first
    assert not keyboard.is_real_key("[")
    assert not keyboard.is_real_key("")

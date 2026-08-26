"""No database needed. Make security.py pass these."""

import security


def test_hash_is_not_the_password():
    hashed = security.hash_password("password123")
    assert hashed != "password123"
    assert "password123" not in hashed


def test_correct_password_verifies():
    hashed = security.hash_password("password123")
    assert security.verify_password("password123", hashed) is True


def test_wrong_password_does_not_verify():
    hashed = security.hash_password("password123")
    assert security.verify_password("wrongpassword", hashed) is False


def test_same_password_hashes_differently():
    # bcrypt salts each hash, so two hashes of the same password differ.
    # if this fails you're probably not salting
    assert security.hash_password("hunter22") != security.hash_password("hunter22")


def test_tokens_are_unique():
    tokens = {security.new_session_token() for _ in range(100)}
    assert len(tokens) == 100


def test_tokens_are_long_enough():
    assert len(security.new_session_token()) >= 32

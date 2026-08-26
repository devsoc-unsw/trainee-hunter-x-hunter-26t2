"""Password hashing and session tokens.

Never store a raw password. bcrypt is already installed:

    import bcrypt
    bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    bcrypt.checkpw(password.encode(), hashed.encode())

bcrypt works on bytes, our column is text, so you'll be doing .encode()
and .decode() a fair bit.
"""

import secrets  # noqa: F401  (you'll want this for new_session_token)

TOKEN_BYTES = 32


def hash_password(password: str) -> str:
    # bcrypt hash the password, return it as a string to store in users.password_hash
    raise NotImplementedError


def verify_password(password: str, password_hash: str) -> bool:
    # True if password matches the hash. must not raise on a wrong password
    raise NotImplementedError


def new_session_token() -> str:
    # random unguessable string for the sessions table. secrets, not random
    raise NotImplementedError

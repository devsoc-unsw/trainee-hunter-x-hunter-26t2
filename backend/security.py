"""Password hashing and session tokens.

Never store a raw password. bcrypt is already installed:

    import bcrypt
    bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    bcrypt.checkpw(password.encode(), hashed.encode())

bcrypt works on bytes, our column is text, so you'll be doing .encode()
and .decode() a fair bit.
"""

import secrets

import bcrypt

TOKEN_BYTES = 32


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        # malformed/foreign hash in the column - treat as no match, don't crash login
        return False


def new_session_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)

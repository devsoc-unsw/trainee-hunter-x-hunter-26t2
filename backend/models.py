"""Request and response shapes.

These are done for you. FastAPI uses them to validate what comes in and to
build the /docs page. If a route returns something that doesn't match its
response_model you get a 500, so these are the contract the frontend can
rely on.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ---------- auth ----------


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


# ---------- users ----------


class User(BaseModel):
    """A user row, minus the password hash."""

    id: UUID
    username: str
    coins: int
    # keys bought with coins. keyboard.py turns this into the number actually
    # unlocked by adding the ones everyone starts with.
    keys_bought: int


class Me(BaseModel):
    """What GET /users/me returns. Everything the header + keyboard need."""

    id: UUID
    username: str
    coins: int
    solved_count: int
    unlocked_keys: int


class UpdateMeRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)


# ---------- questions ----------


class TestCase(BaseModel):
    # tells pytest this isn't a test class, it just has Test in the name
    __test__ = False

    input: list[Any]
    expected: Any


class QuestionSummary(BaseModel):
    """A row in the problem list."""

    id: UUID
    slug: str
    name: str
    difficulty: str
    solved: bool


class QuestionDetail(BaseModel):
    """The problem page. samples only - never send the hidden test cases."""

    id: UUID
    slug: str
    name: str
    details: str
    difficulty: str
    function_name: str
    starter_code: str
    samples: list[TestCase]
    solved: bool


# ---------- submissions ----------


class SubmitRequest(BaseModel):
    code: str


class TestResult(BaseModel):
    passed: bool
    input: list[Any]
    expected: Any
    got: Any = None
    error: str | None = None


class SubmitResponse(BaseModel):
    passed: bool
    results: list[TestResult]
    coins_earned: int
    # true only the first time you solve it
    first_solve: bool


# ---------- shop ----------


class ShopItem(BaseModel):
    id: UUID
    # stable name for the item, eg 'blue-tulip'. the frontend picks its
    # drawing off this, not off image_url - see seed.sql.
    slug: str
    name: str
    price: int
    image_url: str
    # 'key_skin' recolours a key, 'accessory' sits on one
    kind: str
    # 'land' or 'water'. an accessory only goes on a key of the same habitat,
    # which is what keeps the fish off the flowerbeds - see decor.py.
    habitat: str
    owned: bool


class BuyResponse(BaseModel):
    item_id: UUID
    coins_left: int

"""Needs postgres running. Covers backend/queries/*.py directly.

These sit between tests/unit (no database) and tests/api (needs the whole app):
they need the database but not the routers, so they pass today while the
routers are still stubs. If one of these fails, the bug is in the SQL, not in
a route.

    docker compose up -d database
    uv run pytest tests/db
"""

from uuid import UUID

import psycopg
import pytest

import queries.progress
import queries.questions
import queries.sessions
import queries.shop
import queries.users
from models import TestCase, User

MISSING = UUID("00000000-0000-0000-0000-000000000000")


@pytest.fixture
async def user(conn) -> User:
    return await queries.users.create_user(conn, "querytester", "fakehash")


@pytest.fixture
async def two_sum(conn) -> dict:
    questions = await queries.questions.list_questions(conn)
    return next(q for q in questions if q["slug"] == "two-sum")


@pytest.fixture
async def item(conn) -> dict:
    return (await queries.shop.list_items(conn))[0]


# ---------- users ----------


async def test_create_user_starts_with_no_coins(user):
    assert user.username == "querytester"
    assert user.coins == 0


async def test_create_user_rejects_a_duplicate_username(conn, user):
    # the route catches this and turns it into a 409, so it must reach it
    with pytest.raises(psycopg.errors.UniqueViolation):
        await queries.users.create_user(conn, user.username, "otherhash")


async def test_get_user_by_username_includes_the_hash(conn, user):
    """Login needs the hash, so this one returns the raw row."""
    row = await queries.users.get_user_by_username(conn, "querytester")
    assert row is not None
    assert row["password_hash"] == "fakehash"


async def test_get_user_by_username_is_none_when_missing(conn):
    assert await queries.users.get_user_by_username(conn, "nobody") is None


async def test_get_user_by_id_never_returns_the_hash(conn, user):
    found = await queries.users.get_user_by_id(conn, user.id)
    assert found == user
    assert not hasattr(found, "password_hash")


async def test_get_user_by_id_is_none_when_missing(conn):
    assert await queries.users.get_user_by_id(conn, MISSING) is None


async def test_set_username(conn, user):
    await queries.users.set_username(conn, user.id, "renamed")
    found = await queries.users.get_user_by_id(conn, user.id)
    assert found is not None
    assert found.username == "renamed"


async def test_add_coins_returns_the_new_balance(conn, user):
    assert await queries.users.add_coins(conn, user.id, 30) == 30
    assert await queries.users.add_coins(conn, user.id, 20) == 50


async def test_spend_coins_deducts(conn, user):
    await queries.users.add_coins(conn, user.id, 100)
    assert await queries.users.spend_coins(conn, user.id, 60) == 40


async def test_spend_coins_refuses_to_overdraw(conn, user):
    await queries.users.add_coins(conn, user.id, 10)
    assert await queries.users.spend_coins(conn, user.id, 11) is None
    # and it must not have taken anything
    found = await queries.users.get_user_by_id(conn, user.id)
    assert found is not None
    assert found.coins == 10


async def test_spend_coins_allows_spending_the_exact_balance(conn, user):
    await queries.users.add_coins(conn, user.id, 25)
    assert await queries.users.spend_coins(conn, user.id, 25) == 0


# ---------- sessions ----------


async def test_session_round_trip(conn, user):
    await queries.sessions.create_session(conn, user.id, "token-abc")
    assert await queries.sessions.get_user_for_token(conn, "token-abc") == user


async def test_unknown_token_has_no_user(conn):
    assert await queries.sessions.get_user_for_token(conn, "not-a-token") is None


async def test_deleting_a_session_kills_the_token(conn, user):
    await queries.sessions.create_session(conn, user.id, "token-abc")
    await queries.sessions.delete_session(conn, "token-abc")
    assert await queries.sessions.get_user_for_token(conn, "token-abc") is None


async def test_deleting_an_unknown_token_is_not_an_error(conn):
    await queries.sessions.delete_session(conn, "never-existed")


# ---------- questions ----------


async def test_lists_the_seeded_questions(conn):
    questions = await queries.questions.list_questions(conn)
    slugs = {q["slug"] for q in questions}
    assert {"two-sum", "reverse-string"} <= slugs


async def test_question_list_is_ordered_by_name(conn):
    names = [q["name"] for q in await queries.questions.list_questions(conn)]
    assert names == sorted(names)


async def test_question_list_is_only_the_summary_columns(conn):
    """The list page doesn't need details/starter_code, so don't ship them."""
    questions = await queries.questions.list_questions(conn)
    assert set(questions[0]) == {"id", "slug", "name", "difficulty"}


async def test_get_question_returns_the_full_row(conn, two_sum):
    question = await queries.questions.get_question(conn, two_sum["id"])
    assert question is not None
    assert question["function_name"] == "two_sum"
    assert question["starter_code"]
    assert question["details"]


async def test_get_question_is_none_when_missing(conn):
    assert await queries.questions.get_question(conn, MISSING) is None


async def test_test_cases_come_back_as_models(conn, two_sum):
    cases = await queries.questions.get_test_cases(conn, two_sum["id"])
    assert cases
    assert all(isinstance(case, TestCase) for case in cases)
    # jsonb decodes to real python, and input is the argument list
    assert isinstance(cases[0].input, list)


async def test_samples_only_hides_the_grading_cases(conn, two_sum):
    """The question page must never receive the hidden test cases."""
    everything = await queries.questions.get_test_cases(conn, two_sum["id"])
    samples = await queries.questions.get_test_cases(
        conn, two_sum["id"], samples_only=True
    )
    assert 0 < len(samples) < len(everything)


# ---------- progress ----------


async def test_mark_solved_only_reports_the_first_time(conn, user, two_sum):
    # this is what tells the route whether to pay out
    assert await queries.progress.mark_solved(conn, user.id, two_sum["id"]) is True
    assert await queries.progress.mark_solved(conn, user.id, two_sum["id"]) is False


async def test_has_solved_flips_after_a_solve(conn, user, two_sum):
    assert await queries.progress.has_solved(conn, user.id, two_sum["id"]) is False
    await queries.progress.mark_solved(conn, user.id, two_sum["id"])
    assert await queries.progress.has_solved(conn, user.id, two_sum["id"]) is True


async def test_list_solved_ids(conn, user, two_sum):
    assert await queries.progress.list_solved_ids(conn, user.id) == set()
    await queries.progress.mark_solved(conn, user.id, two_sum["id"])
    assert await queries.progress.list_solved_ids(conn, user.id) == {two_sum["id"]}


async def test_count_solved(conn, user, two_sum):
    assert await queries.progress.count_solved(conn, user.id) == 0
    await queries.progress.mark_solved(conn, user.id, two_sum["id"])
    assert await queries.progress.count_solved(conn, user.id) == 1


# ---------- shop ----------


async def test_shop_lists_cheapest_first(conn):
    prices = [row["price"] for row in await queries.shop.list_items(conn)]
    assert len(prices) >= 4
    assert prices == sorted(prices)


async def test_get_item(conn, item):
    found = await queries.shop.get_item(conn, item["id"])
    assert found is not None
    assert found["name"] == item["name"]


async def test_get_item_is_none_when_missing(conn):
    assert await queries.shop.get_item(conn, MISSING) is None


async def test_buying_flips_ownership(conn, user, item):
    assert await queries.shop.owns_item(conn, user.id, item["id"]) is False
    await queries.shop.add_to_inventory(conn, user.id, item["id"])
    assert await queries.shop.owns_item(conn, user.id, item["id"]) is True


async def test_cannot_own_the_same_item_twice(conn, user, item):
    # the route turns the False into a 409
    assert await queries.shop.add_to_inventory(conn, user.id, item["id"]) is True
    assert await queries.shop.add_to_inventory(conn, user.id, item["id"]) is False


async def test_inventory_joins_through_to_the_item(conn, user, item):
    assert await queries.shop.list_inventory(conn, user.id) == []
    await queries.shop.add_to_inventory(conn, user.id, item["id"])
    owned = await queries.shop.list_inventory(conn, user.id)
    assert [row["id"] for row in owned] == [item["id"]]
    assert owned[0]["name"] == item["name"]
    assert "price" in owned[0]

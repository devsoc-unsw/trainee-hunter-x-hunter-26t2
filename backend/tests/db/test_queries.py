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

import queries.decor
import queries.keypresses
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


# ---------- decor ----------


@pytest.fixture
async def owned(conn, user):
    """Gives the user one of everything, so placement tests can place it."""
    items = {row["slug"]: row for row in await queries.shop.list_items(conn)}
    for slug in ("soil-key", "water-key", "fish", "blue-tulip"):
        await queries.shop.add_to_inventory(conn, user.id, items[slug]["id"])
    return items


async def test_a_fresh_keyboard_has_no_decor(conn, user):
    # no rows at all - the frontend draws every key as the default grass
    assert await queries.decor.list_key_decor(conn, user.id) == []


async def test_cannot_place_an_item_you_do_not_own(conn, user):
    """The composite foreign key is what enforces this, not route code."""
    fish = next(
        row for row in await queries.shop.list_items(conn) if row["slug"] == "fish"
    )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        await queries.decor.set_accessory(conn, user.id, "f", fish["id"])


async def test_decor_reads_back_as_slugs(conn, user, owned):
    await queries.decor.set_skin(
        conn, user.id, "f", owned["water-key"]["id"], keep_accessory=False
    )
    await queries.decor.set_accessory(conn, user.id, "f", owned["fish"]["id"])

    decor = await queries.decor.list_key_decor(conn, user.id)
    assert decor == [
        {"key_char": "f", "skin_slug": "water-key", "accessory_slug": "fish"}
    ]


async def test_a_second_accessory_replaces_the_first(conn, user, owned):
    # one accessory per key. the primary key is what makes this a replace
    # rather than two flowers piling up on the same key
    await queries.decor.set_accessory(conn, user.id, "f", owned["fish"]["id"])
    await queries.decor.set_accessory(conn, user.id, "f", owned["blue-tulip"]["id"])

    decor = await queries.decor.list_key_decor(conn, user.id)
    assert len(decor) == 1
    assert decor[0]["accessory_slug"] == "blue-tulip"


async def test_changing_skin_can_evict_an_incompatible_accessory(conn, user, owned):
    """A fish on a key that stops being water has to go somewhere."""
    await queries.decor.set_skin(
        conn, user.id, "f", owned["water-key"]["id"], keep_accessory=False
    )
    await queries.decor.set_accessory(conn, user.id, "f", owned["fish"]["id"])

    await queries.decor.set_skin(
        conn, user.id, "f", owned["soil-key"]["id"], keep_accessory=False
    )
    decor = await queries.decor.list_key_decor(conn, user.id)
    assert decor[0]["skin_slug"] == "soil-key"
    assert decor[0]["accessory_slug"] is None


async def test_changing_skin_can_keep_a_compatible_accessory(conn, user, owned):
    await queries.decor.set_accessory(conn, user.id, "f", owned["blue-tulip"]["id"])
    await queries.decor.set_skin(
        conn, user.id, "f", owned["soil-key"]["id"], keep_accessory=True
    )
    decor = await queries.decor.list_key_decor(conn, user.id)
    assert decor[0]["accessory_slug"] == "blue-tulip"


async def test_clearing_a_key(conn, user, owned):
    await queries.decor.set_accessory(conn, user.id, "f", owned["fish"]["id"])
    assert await queries.decor.clear_key(conn, user.id, "f") is True
    assert await queries.decor.list_key_decor(conn, user.id) == []
    # clearing a key that was never decorated is not an error
    assert await queries.decor.clear_key(conn, user.id, "f") is False


async def test_decor_is_per_user(conn, user, owned):
    other = await queries.users.create_user(conn, "someoneelse", "fakehash")
    await queries.decor.set_accessory(conn, user.id, "f", owned["fish"]["id"])
    assert await queries.decor.list_key_decor(conn, other.id) == []


# ---------- key presses ----------


async def test_presses_start_at_one_and_climb(conn, user):
    assert await queries.keypresses.record_press(conn, user.id, "f") == 1
    assert await queries.keypresses.record_press(conn, user.id, "f") == 2
    assert await queries.keypresses.record_press(conn, user.id, "f") == 3


async def test_presses_are_counted_per_key(conn, user):
    await queries.keypresses.record_press(conn, user.id, "f")
    await queries.keypresses.record_press(conn, user.id, "f")
    await queries.keypresses.record_press(conn, user.id, "j")

    assert await queries.keypresses.list_presses(conn, user.id) == {"f": 2, "j": 1}
    assert await queries.keypresses.total_presses(conn, user.id) == 3


async def test_presses_are_per_user(conn, user):
    """The in-memory version this replaces counted everyone into one dict."""
    other = await queries.users.create_user(conn, "someoneelse", "fakehash")
    await queries.keypresses.record_press(conn, user.id, "f")
    assert await queries.keypresses.record_press(conn, other.id, "f") == 1
    assert await queries.keypresses.list_presses(conn, other.id) == {"f": 1}


async def test_no_presses_yet(conn, user):
    assert await queries.keypresses.list_presses(conn, user.id) == {}
    assert await queries.keypresses.total_presses(conn, user.id) == 0


# ---------- buying key unlocks ----------


async def test_new_user_has_bought_no_keys(user):
    assert user.keys_bought == 0


async def test_buying_a_key_costs_coins(conn, user):
    await queries.users.add_coins(conn, user.id, 100)
    row = await queries.users.buy_key_unlock(conn, user.id, price=40, max_keys=36)
    assert row is not None
    assert row == {"coins": 60, "keys_bought": 1}


async def test_cannot_buy_a_key_you_cannot_afford(conn, user):
    await queries.users.add_coins(conn, user.id, 10)
    assert await queries.users.buy_key_unlock(conn, user.id, price=40, max_keys=36) is None
    # and it must not have charged them or half-unlocked anything
    after = await queries.users.get_user_by_id(conn, user.id)
    assert after is not None
    assert (after.coins, after.keys_bought) == (10, 0)


async def test_cannot_buy_past_the_end_of_the_keyboard(conn, user):
    await queries.users.add_coins(conn, user.id, 1000)
    assert await queries.users.buy_key_unlock(conn, user.id, price=1, max_keys=2) is not None
    assert await queries.users.buy_key_unlock(conn, user.id, price=1, max_keys=2) is not None
    assert await queries.users.buy_key_unlock(conn, user.id, price=1, max_keys=2) is None

    after = await queries.users.get_user_by_id(conn, user.id)
    assert after is not None
    assert (after.coins, after.keys_bought) == (998, 2)

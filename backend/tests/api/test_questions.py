"""Needs postgres running. Make routers/questions.py pass these."""

import pytest


@pytest.fixture
async def two_sum(client, auth) -> dict:
    questions = (await client.get("/questions", headers=auth)).json()
    return next(q for q in questions if q["slug"] == "two-sum")


async def test_listing_needs_a_login(client):
    assert (await client.get("/questions")).status_code == 401


async def test_lists_the_seeded_questions(client, auth):
    response = await client.get("/questions", headers=auth)
    assert response.status_code == 200
    slugs = {q["slug"] for q in response.json()}
    assert {"two-sum", "reverse-string"} <= slugs


async def test_nothing_is_solved_for_a_new_user(client, auth):
    questions = (await client.get("/questions", headers=auth)).json()
    assert all(q["solved"] is False for q in questions)


async def test_question_detail(client, auth, two_sum):
    response = await client.get(f"/questions/{two_sum['id']}", headers=auth)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Two Sum"
    assert body["function_name"] == "two_sum"
    assert body["starter_code"]


async def test_detail_only_shows_sample_test_cases(client, auth, two_sum, conn):
    """Hidden test cases must not go over the wire, people can read the response."""
    body = (await client.get(f"/questions/{two_sum['id']}", headers=auth)).json()
    total = await (
        await conn.execute(
            "select count(*) as n from test_cases where question_id = %s",
            (two_sum["id"],),
        )
    ).fetchone()
    assert len(body["samples"]) < total["n"]


async def test_unknown_question_is_404(client, auth):
    response = await client.get(
        "/questions/00000000-0000-0000-0000-000000000000", headers=auth
    )
    assert response.status_code == 404

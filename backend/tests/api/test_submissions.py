"""Needs postgres running. Make routers/submissions.py pass these.

judge.py has to work before these can.
"""

import pytest

GOOD = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
"""

BAD = """
def two_sum(nums, target):
    return [0, 0]
"""


@pytest.fixture
async def question_id(client, auth) -> str:
    questions = (await client.get("/questions", headers=auth)).json()
    return next(q["id"] for q in questions if q["slug"] == "two-sum")


async def test_correct_solution_passes(client, auth, question_id):
    response = await client.post(
        f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
    )
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] is True
    assert all(r["passed"] for r in body["results"])


async def test_wrong_solution_fails_but_still_returns_results(
    client, auth, question_id
):
    response = await client.post(
        f"/questions/{question_id}/submit", json={"code": BAD}, headers=auth
    )
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] is False
    assert len(body["results"]) > 1  # they want to see every test, not just the first


async def test_solving_pays_coins(client, auth, question_id):
    body = (
        await client.post(
            f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
        )
    ).json()
    assert body["first_solve"] is True
    assert body["coins_earned"] > 0
    assert (await client.get("/users/me", headers=auth)).json()["coins"] > 0


async def test_solving_twice_pays_nothing(client, auth, question_id):
    await client.post(
        f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
    )
    coins_after_first = (await client.get("/users/me", headers=auth)).json()["coins"]

    body = (
        await client.post(
            f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
        )
    ).json()
    assert body["first_solve"] is False
    assert body["coins_earned"] == 0
    assert (
        await client.get("/users/me", headers=auth)
    ).json()["coins"] == coins_after_first


async def test_failing_pays_nothing(client, auth, question_id):
    body = (
        await client.post(
            f"/questions/{question_id}/submit", json={"code": BAD}, headers=auth
        )
    ).json()
    assert body["coins_earned"] == 0
    assert (await client.get("/users/me", headers=auth)).json()["coins"] == 0


async def test_solving_grows_the_keyboard(client, auth, question_id):
    # solving earns an unlock CREDIT rather than lighting up the next key in a
    # fixed order - the user spends it on whichever key they want, via
    # POST /keyboard/{key}/unlock. So the keyboard doesn't grow until they do.
    before = (await client.get("/users/me", headers=auth)).json()
    await client.post(
        f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
    )
    after = (await client.get("/users/me", headers=auth)).json()
    assert after["solved_count"] == 1
    assert after["unlock_credits"] == before["unlock_credits"] + 1
    assert after["unlocked_keys"] == before["unlocked_keys"]

    unlocked = await client.post("/keyboard/z/unlock", headers=auth)
    assert unlocked.status_code == 200
    assert "z" in unlocked.json()["unlocked_keys"]
    assert unlocked.json()["unlock_credits"] == 0


async def test_solved_shows_up_in_the_question_list(client, auth, question_id):
    await client.post(
        f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
    )
    questions = (await client.get("/questions", headers=auth)).json()
    assert next(q for q in questions if q["id"] == question_id)["solved"] is True


async def test_submitting_needs_a_login(client, question_id):
    response = await client.post(
        f"/questions/{question_id}/submit", json={"code": GOOD}
    )
    assert response.status_code == 401


async def test_unknown_question_is_404(client, auth):
    response = await client.post(
        "/questions/00000000-0000-0000-0000-000000000000/submit",
        json={"code": GOOD},
        headers=auth,
    )
    assert response.status_code == 404

"""Needs postgres running. The Run button, and what /submit is allowed to show.

tests/api/test_submissions.py covers grading and payout. This file covers the
two things added alongside it: POST /questions/{id}/run (samples only, never
pays), and the redaction that stops one wrong submission dumping the hidden
test cases into the browser.
"""

import pytest

GOOD = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
"""

# wrong on every case, samples included
BAD = """
def two_sum(nums, target):
    return [0, 0]
"""

# right on the sample, wrong on at least one hidden case - the shape that
# makes redaction interesting
SAMPLE_ONLY = """
def two_sum(nums, target):
    return [0, 1]
"""


@pytest.fixture
async def question_id(client, auth) -> str:
    questions = (await client.get("/questions", headers=auth)).json()
    return next(q["id"] for q in questions if q["slug"] == "two-sum")


async def test_run_judges_only_the_samples(client, auth, question_id):
    run = (
        await client.post(
            f"/questions/{question_id}/run", json={"code": GOOD}, headers=auth
        )
    ).json()
    submit = (
        await client.post(
            f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
        )
    ).json()

    samples = (await client.get(f"/questions/{question_id}", headers=auth)).json()
    assert len(run["results"]) == len(samples["samples"])
    assert len(run["results"]) < len(submit["results"])


async def test_running_never_pays_or_records_a_solve(client, auth, question_id):
    body = (
        await client.post(
            f"/questions/{question_id}/run", json={"code": GOOD}, headers=auth
        )
    ).json()
    assert body["passed"] is True

    me = (await client.get("/users/me", headers=auth)).json()
    assert me["coins"] == 0
    assert me["solved_count"] == 0

    questions = (await client.get("/questions", headers=auth)).json()
    assert next(q for q in questions if q["id"] == question_id)["solved"] is False


async def test_run_shows_sample_failures_in_full(client, auth, question_id):
    body = (
        await client.post(
            f"/questions/{question_id}/run", json={"code": BAD}, headers=auth
        )
    ).json()
    assert body["passed"] is False
    # samples are already on the question page, so there is nothing to hide
    assert all(not result["hidden"] for result in body["results"])
    assert all(result["input"] for result in body["results"])


async def test_run_needs_a_login(client, question_id):
    response = await client.post(f"/questions/{question_id}/run", json={"code": GOOD})
    assert response.status_code == 401


async def test_run_unknown_question_is_404(client, auth):
    response = await client.post(
        "/questions/00000000-0000-0000-0000-000000000000/run",
        json={"code": GOOD},
        headers=auth,
    )
    assert response.status_code == 404


async def test_submit_reveals_exactly_one_hidden_failure(client, auth, question_id):
    """Enough to debug with, not enough to be an answer key."""
    detail = (await client.get(f"/questions/{question_id}", headers=auth)).json()
    sample_inputs = [sample["input"] for sample in detail["samples"]]

    body = (
        await client.post(
            f"/questions/{question_id}/submit", json={"code": SAMPLE_ONLY}, headers=auth
        )
    ).json()
    assert body["passed"] is False

    visible = [result for result in body["results"] if not result["hidden"]]
    hidden = [result for result in body["results"] if result["hidden"]]
    assert hidden, "with this many test cases some should have been redacted"

    # a redacted row carries the pass/fail bit and nothing else
    for result in hidden:
        assert result["input"] == []
        assert result["expected"] is None
        assert result["got"] is None

    # of the cases NOT on the question page, exactly one was revealed, and it
    # was a failure - complete enough for the user to act on
    revealed = [
        result for result in visible if result["input"] not in sample_inputs
    ]
    assert len(revealed) == 1
    assert revealed[0]["passed"] is False
    assert revealed[0]["expected"] is not None


async def test_a_passing_submission_reveals_no_hidden_cases(
    client, auth, question_id
):
    detail = (await client.get(f"/questions/{question_id}", headers=auth)).json()

    body = (
        await client.post(
            f"/questions/{question_id}/submit", json={"code": GOOD}, headers=auth
        )
    ).json()
    assert body["passed"] is True

    # nothing failed, so there was no failure worth revealing: the only rows
    # with real data in them are the samples, which were public anyway
    visible = [result for result in body["results"] if not result["hidden"]]
    assert len(visible) == len(detail["samples"])

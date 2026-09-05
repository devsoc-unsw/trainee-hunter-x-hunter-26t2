import asyncio
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

import judge
import rewards
from deps import Conn, CurrentUser
from models import RunResponse, SubmitRequest, SubmitResponse, TestCase, TestResult
from queries.progress import mark_solved
from queries.questions import get_question, get_test_cases
from queries.users import add_coins

router = APIRouter(prefix="/questions", tags=["submissions"])


def visible_results(
    results: list[TestResult], tests: list[TestCase]
) -> list[TestResult]:
    """Blanks the hidden test cases the user isn't entitled to see.

    Sample cases are already on the question page, so they go back in full.
    Of the hidden ones we reveal exactly the FIRST failure - enough to debug
    with ("expected [0, 1], got [0, 0] for input [3, 3], 6"), not enough for
    one wrong submission to hand over the whole answer key.

    This happens on the server on purpose. Filtering it in React would still
    ship every hidden case to the browser, where it's one devtools tab away.
    """
    revealed = False
    shown: list[TestResult] = []

    for result, test in zip(results, tests):
        if test.is_sample:
            shown.append(result)
            continue
        if not result.passed and not revealed:
            revealed = True
            shown.append(result)
            continue
        # pydantic models are immutable-ish here by convention - copy rather
        # than mutate, so the caller's list still has the real values for
        # deciding whether the submission passed.
        shown.append(
            result.model_copy(
                update={"input": [], "expected": None, "got": None, "hidden": True}
            )
        )

    return shown


async def _judge_question(question_id: UUID, code: str, conn: Conn, samples_only: bool):
    """Shared by run and submit: 404, load the tests, judge off the event loop."""
    question = await get_question(conn, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    tests = await get_test_cases(conn, question_id, samples_only=samples_only)

    # to_thread matters. run_submission blocks for up to
    # len(tests) * SECONDS_PER_TEST, and this is an async route - calling it
    # directly would pin the event loop for that whole time, freezing every
    # other request in the app, including the keylogger firing on every
    # keystroke of whoever else is typing.
    results = await asyncio.to_thread(
        judge.run_submission, code, question["function_name"], tests
    )

    # bool(results) guards a question with no test cases: all([]) is True, so
    # without it an empty question would mark itself solved and pay out.
    passed = bool(results) and all(result.passed for result in results)
    return question, tests, results, passed


@router.post("/{question_id}/run", response_model=RunResponse)
async def run(question_id: UUID, body: SubmitRequest, conn: Conn, user: CurrentUser):
    # the Run button: judge against the SAMPLE cases only. no completions row,
    # no coins, nothing written. samples are public, so nothing to redact.
    _, _, results, passed = await _judge_question(
        question_id, body.code, conn, samples_only=True
    )
    return RunResponse(passed=passed, results=results)


@router.post("/{question_id}/submit", response_model=SubmitResponse)
async def submit(question_id: UUID, body: SubmitRequest, conn: Conn, user: CurrentUser):
    question, tests, results, passed = await _judge_question(
        question_id, body.code, conn, samples_only=False
    )

    first_solve = False
    coins_earned = 0

    if passed:
        # mark_solved's `on conflict do nothing ... returning` answers "was
        # this the first time" in the same statement that records the solve.
        # that's the whole pay-once mechanism - don't put a has_solved check
        # in front of it, that's exactly the race it exists to avoid.
        first_solve = await mark_solved(conn, user.id, question_id)
        if first_solve:
            coins_earned = rewards.coins_for_solve(question["difficulty"])
            if coins_earned:
                await add_coins(conn, user.id, coins_earned)

    return SubmitResponse(
        passed=passed,
        results=visible_results(results, tests),
        coins_earned=coins_earned,
        first_solve=first_solve,
    )

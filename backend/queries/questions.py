from uuid import UUID

import psycopg

from models import TestCase


async def list_questions(conn: psycopg.AsyncConnection) -> list[dict]:
    # every question, id/slug/name/difficulty. order by name so the list
    # doesn't shuffle between page loads
    raise NotImplementedError


async def get_question(conn: psycopg.AsyncConnection, question_id: UUID) -> dict | None:
    # the full row. None if it doesn't exist
    raise NotImplementedError


async def get_test_cases(
    conn: psycopg.AsyncConnection, question_id: UUID, samples_only: bool = False
) -> list[TestCase]:
    # test cases for a question. samples_only=True for the question page,
    # False when judging a submission
    raise NotImplementedError

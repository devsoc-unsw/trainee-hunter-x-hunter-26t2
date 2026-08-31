from uuid import UUID

import psycopg
from psycopg.rows import DictRow

from models import TestCase


async def list_questions(conn: psycopg.AsyncConnection[DictRow]) -> list[dict]:
    # every question, id/slug/name/difficulty. order by name so the list
    # doesn't shuffle between page loads
    return await (
        await conn.execute(
            "select id, slug, name, difficulty from questions order by name"
        )
    ).fetchall()


async def get_question(conn: psycopg.AsyncConnection[DictRow], question_id: UUID) -> dict | None:
    # the full row. None if it doesn't exist
    return await (
        await conn.execute("select * from questions where id = %s", (question_id,))
    ).fetchone()


async def get_test_cases(
    conn: psycopg.AsyncConnection[DictRow], question_id: UUID, samples_only: bool = False
) -> list[TestCase]:
    # test cases for a question. samples_only=True for the question page,
    # False when judging a submission
    sql = "select input, expected from test_cases where question_id = %s"
    if samples_only:
        sql += " and is_sample = true"
    rows = await (await conn.execute(sql, (question_id,))).fetchall()
    return [TestCase(**row) for row in rows]

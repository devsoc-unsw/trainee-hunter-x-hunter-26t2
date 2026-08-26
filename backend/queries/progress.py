from uuid import UUID

import psycopg


async def mark_solved(
    conn: psycopg.AsyncConnection, user_id: UUID, question_id: UUID
) -> bool:
    # record a solve. returns True if this is the FIRST time (so the route
    # knows whether to pay out). look up 'on conflict do nothing' - it makes
    # this one query instead of a check-then-insert race
    raise NotImplementedError


async def has_solved(
    conn: psycopg.AsyncConnection, user_id: UUID, question_id: UUID
) -> bool:
    raise NotImplementedError


async def list_solved_ids(
    conn: psycopg.AsyncConnection, user_id: UUID
) -> set[UUID]:
    # every question id this user has solved. a set so the questions route
    # can check membership cheaply
    raise NotImplementedError


async def count_solved(conn: psycopg.AsyncConnection, user_id: UUID) -> int:
    # how many solved, drives the keyboard size
    raise NotImplementedError

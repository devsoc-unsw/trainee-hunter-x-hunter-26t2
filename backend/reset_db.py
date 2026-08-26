"""Nukes the database and rebuilds it from scratch.

    uv run python reset_db.py

Runs schema.sql, then seed.sql (shop items), then load_questions.py.
DELETES ALL USER ACCOUNTS. If you only changed the question csvs, run
load_questions.py instead.
"""

import pathlib

import psycopg

import load_questions
from db import database_url

HERE = pathlib.Path(__file__).parent


def run_sql_file(cursor: psycopg.Cursor, name: str) -> None:
    cursor.execute((HERE / name).read_text(encoding="utf-8"))


def reset() -> None:
    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            run_sql_file(cursor, "schema.sql")
            run_sql_file(cursor, "seed.sql")
    print("schema rebuilt, shop seeded")

    load_questions.load()


if __name__ == "__main__":
    reset()

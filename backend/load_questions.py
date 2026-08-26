"""Loads the question bank from data/*.csv into the database.

    uv run python load_questions.py

Wipes questions + test_cases and reinserts from the csvs. User accounts,
coins and inventory are left alone. Completions get cascade deleted though,
since the question rows they point at are gone.
"""

import csv
import json
import pathlib
import sys

import psycopg

from db import database_url

DATA_DIR = pathlib.Path(__file__).parent / "data"
QUESTIONS_CSV = DATA_DIR / "questions.csv"
TEST_CASES_CSV = DATA_DIR / "test_cases.csv"

DIFFICULTIES = {"easy", "medium", "hard"}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "y"}


def check_questions(rows: list[dict[str, str]]) -> None:
    """Yells about bad csv rows before we touch the database."""
    seen = set()
    for line, row in enumerate(rows, start=2):
        slug = (row.get("slug") or "").strip()
        if not slug:
            sys.exit(f"questions.csv line {line}: missing slug")
        if slug in seen:
            sys.exit(f"questions.csv line {line}: duplicate slug '{slug}'")
        seen.add(slug)

        difficulty = (row.get("difficulty") or "").strip().lower()
        if difficulty not in DIFFICULTIES:
            sys.exit(
                f"questions.csv line {line}: difficulty must be one of "
                f"{sorted(DIFFICULTIES)}, got '{difficulty}'"
            )
        if not (row.get("function_name") or "").strip():
            sys.exit(f"questions.csv line {line}: missing function_name")


def check_test_cases(rows: list[dict[str, str]], slugs: set[str]) -> None:
    for line, row in enumerate(rows, start=2):
        slug = (row.get("slug") or "").strip()
        if slug not in slugs:
            sys.exit(
                f"test_cases.csv line {line}: slug '{slug}' is not in questions.csv"
            )
        for column in ("input", "expected"):
            try:
                json.loads(row[column])
            except (KeyError, json.JSONDecodeError) as error:
                sys.exit(f"test_cases.csv line {line}: bad {column} json - {error}")

    without_tests = slugs - {(row.get("slug") or "").strip() for row in rows}
    if without_tests:
        print(f"warning: no test cases for {sorted(without_tests)}")


def load() -> None:
    questions = read_csv(QUESTIONS_CSV)
    test_cases = read_csv(TEST_CASES_CSV)

    check_questions(questions)
    check_test_cases(test_cases, {row["slug"].strip() for row in questions})

    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            # test_cases go too, they cascade off questions
            cursor.execute("delete from questions")

            ids: dict[str, str] = {}
            for row in questions:
                cursor.execute(
                    """
                    insert into questions
                        (slug, name, details, difficulty, function_name, starter_code)
                    values (%s, %s, %s, %s, %s, %s)
                    returning id
                    """,
                    (
                        row["slug"].strip(),
                        row["name"].strip(),
                        row["details"],
                        row["difficulty"].strip().lower(),
                        row["function_name"].strip(),
                        row.get("starter_code", ""),
                    ),
                )
                ids[row["slug"].strip()] = cursor.fetchone()[0]

            for row in test_cases:
                cursor.execute(
                    """
                    insert into test_cases (question_id, input, expected, is_sample)
                    values (%s, %s, %s, %s)
                    """,
                    (
                        ids[row["slug"].strip()],
                        row["input"],
                        row["expected"],
                        parse_bool(row.get("is_sample", "false")),
                    ),
                )

    print(f"loaded {len(questions)} questions, {len(test_cases)} test cases")


if __name__ == "__main__":
    load()

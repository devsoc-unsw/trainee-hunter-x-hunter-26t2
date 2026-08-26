"""Test setup. This is done for you.

Tests that need a database run against `trainee_hunter_test`, NOT your real
one, so running them can't eat your data. The database is created and the
schema rebuilt once per test run.

    docker compose up -d database   # postgres has to be running
    uv run pytest

Tests in tests/unit/ don't touch the database at all and work without it.
"""

import pathlib

import psycopg
import pytest
from httpx import ASGITransport, AsyncClient

import load_questions
from db import get_conn

BACKEND_DIR = pathlib.Path(__file__).parent.parent
TEST_DB = "trainee_hunter_test"
ADMIN_URL = "postgresql://app:app@localhost:5432/postgres"
TEST_URL = f"postgresql://app:app@localhost:5432/{TEST_DB}"


def _create_test_database() -> None:
    with psycopg.connect(ADMIN_URL, autocommit=True) as connection:
        exists = connection.execute(
            "select 1 from pg_database where datname = %s", (TEST_DB,)
        ).fetchone()
        if not exists:
            connection.execute(f'create database "{TEST_DB}"')


@pytest.fixture(scope="session")
def test_database() -> str:
    """Builds the test database once, returns its url."""
    try:
        _create_test_database()
    except psycopg.OperationalError as error:
        pytest.skip(f"no postgres running ({error})")

    with psycopg.connect(TEST_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute((BACKEND_DIR / "schema.sql").read_text())
            cursor.execute((BACKEND_DIR / "seed.sql").read_text())

    load_questions.database_url = lambda: TEST_URL
    load_questions.load()
    return TEST_URL


@pytest.fixture
async def conn(test_database: str):
    """A connection that rolls back at the end, so tests don't leak data."""
    from psycopg.rows import dict_row

    async with await psycopg.AsyncConnection.connect(
        test_database, row_factory=dict_row
    ) as connection:
        yield connection
        await connection.rollback()


@pytest.fixture
async def client(conn):
    """An http client talking to the app, sharing the test transaction."""
    from main import app

    async def override():
        yield conn

    app.dependency_overrides[get_conn] = override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
    app.dependency_overrides.clear()


@pytest.fixture
async def user_token(client) -> str:
    """Signs up a user and returns their token, for tests that need a login."""
    response = await client.post(
        "/auth/signup", json={"username": "tester", "password": "password123"}
    )
    return response.json()["token"]


@pytest.fixture
def auth(user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}

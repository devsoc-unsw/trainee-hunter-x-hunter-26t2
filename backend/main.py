import os

import psycopg
from fastapi import FastAPI, HTTPException


app = FastAPI(title="Trainee Hunter API")


def database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://app:app@localhost:5432/trainee_hunter",
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    try:
        async with await psycopg.AsyncConnection.connect(database_url()) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                await cursor.fetchone()
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="Database is unavailable") from error

    return {"status": "ok", "database": "connected"}

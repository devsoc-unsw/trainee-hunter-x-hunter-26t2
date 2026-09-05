"""App entry point. This one is done for you - add new routers here.

    uv run fastapi dev main.py

Then open http://localhost:8000/docs to poke at the routes.
"""

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import database_url
from routers import auth, questions, shop, submissions, users, keylogger, decor

app = FastAPI(title="Trainee Hunter API")

# the vite dev server runs on a different port, so the browser blocks requests
# to us unless we say it's allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(questions.router)
app.include_router(submissions.router)
app.include_router(shop.router)
app.include_router(keylogger.router)
app.include_router(decor.router)


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

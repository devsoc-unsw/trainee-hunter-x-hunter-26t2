# trainee-hunter-x-hunter-26t2

A leetcode tracker where your keyboard grows as you solve problems.

## Local development (day to day)

You need: Docker, [uv](https://docs.astral.sh/uv/), and **Node 20+**
(check with `node -v` - vite won't start on 18).

Run each of these in its own terminal:

```sh
# 1. just the database in docker
docker compose up database

# 2. the api - http://localhost:8000/docs lists every route
cd backend
uv run fastapi dev main.py

# 3. the frontend - http://localhost:5173
cd frontend
npm install
npm run dev
```

First time (and any time you change `schema.sql`):

```sh
cd backend
uv run python reset_db.py     # WIPES everything, rebuilds tables + shop + questions
```

Changed the question csvs in `backend/data/`? This reloads them without
touching user accounts:

```sh
uv run python load_questions.py
```

## Tests

The backend tests are the todo list - they describe what each stub should do,
and they're all supposed to fail until you implement things. Work until your
file's tests go green.

```sh
cd backend
uv run pytest               # everything (needs the database running)
uv run pytest tests/unit    # just the no-database ones
uv run pytest tests/api/test_auth.py -x   # one file, stop at first failure
```

The frontend has no tests - check your work in the browser.

## Where things live

```
backend/
  routers/     http routes - one file per feature
  queries/     all the SQL
  judge.py     runs submitted code (READ THE WARNING IN IT)
  keyboard.py  how many keys you've unlocked
  data/        the question bank as csvs
  tests/       the spec
frontend/src/
  api/         one function per backend route
  pages/       one file per screen
  components/  navbar, keyboard, editor, test results
  auth/        login state (useAuth hook)
```

## Run with Docker

The Docker Compose stack starts:

- the React frontend at <http://localhost:3000>
- the FastAPI backend at <http://localhost:8000>
- PostgreSQL on `localhost:5432`

Start the full application:

```sh
docker compose up --build
```

The frontend proxies requests under `/api` to the backend. For example,
<http://localhost:3000/api/health> checks both the API and its database
connection.

To customize ports or database credentials, copy `.env.example` to `.env`
and edit it before starting the stack. The PostgreSQL data is retained in the
named `postgres_data` volume.

Stop the services with:

```sh
docker compose down
```

To also delete the local database data, run `docker compose down --volumes`.

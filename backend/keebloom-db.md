# Keebloom Database Schema

Postgres schema for this project's own database (the `database` service in
[`compose.yaml`](../compose.yaml)) - no external auth or storage service.
Authentication is handled directly by the FastAPI backend: passwords are
bcrypt-hashed and checked in [`security.py`](./security.py), and login
sessions are plain rows in the `sessions` table, not JWTs from a third-party
provider.

See [`keebloom-db-schema.excalidraw`](./keebloom-db-schema.excalidraw) in this folder for visual.

Schema is applied by running [`schema.sql`](./schema.sql) directly - that's
the source of truth; this doc is a readable summary of it. To change a table,
edit `schema.sql` and re-run `uv run python reset_db.py`, which drops and
rebuilds every table (see the root [README](../README.md) for the full
local-dev flow).

This describes what's actually in `schema.sql` right now - what the current
routers, queries, and tests are built against. See
[Deferred / not built yet](#deferred--not-built-yet) at the bottom for ideas
that aren't implemented.

## Overview

| Table | Purpose |
|---|---|
| [`users`](#users) | Account data - username, password hash, coin balance |
| [`sessions`](#sessions) | Login tokens, one row per logged-in device |
| [`questions`](#questions) | Coding problems |
| [`test_cases`](#test_cases) | Grading inputs/outputs for each question |
| [`completions`](#completions) | Which user solved which question |
| [`shop_items`](#shop_items) | Catalog of purchasable cosmetics |
| [`inventory`](#inventory) | What each user has bought |

---

## `users`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `username` | `text` | not null, unique | |
| `password_hash` | `text` | not null | bcrypt hash, set/checked in [`security.py`](./security.py) |
| `coins` | `integer` | not null, default `0`, check `>= 0` | In-game currency balance, mutated in place (no ledger) |
| `created_at` | `timestamptz` | not null, default `now()` | |

`POST /auth/signup` ([`routers/auth.py`](./routers/auth.py)) is the only
thing that creates a row here.

## `sessions`

One row per logged-in device; logging out deletes the row. This is the
entire session mechanism - no JWTs, no external auth provider.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `token` | `text` | PK | Random, unguessable - see `new_session_token()` in [`security.py`](./security.py) |
| `user_id` | `uuid` | not null, -> `users(id)` on delete cascade | |
| `created_at` | `timestamptz` | not null, default `now()` | |

## `questions`

Admin-authored coding problems.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `slug` | `text` | not null, unique | URL-friendly identifier, e.g. `two-sum`; also links the two CSVs in `data/` |
| `name` | `text` | not null | |
| `details` | `text` | not null | Problem statement |
| `difficulty` | `text` | not null, check ∈ `easy`/`medium`/`hard` | |
| `function_name` | `text` | not null | The function the submitted code must define, e.g. `two_sum` - `judge.py` calls this by name to grade a submission |
| `starter_code` | `text` | not null, default `''` | Prefilled editor content |

## `test_cases`

Inputs/outputs used to grade submissions for a question.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `question_id` | `uuid` | not null, -> `questions(id)` on delete cascade | |
| `input` | `jsonb` | not null | Argument list, e.g. `[[2,7,11,15], 9]` |
| `expected` | `jsonb` | not null | Expected return value |
| `is_sample` | `boolean` | not null, default `false` | `true` = shown on the question page as an example; `false` = hidden grading case |

## `completions`

One row per question a user has solved; no row means not solved yet.
Submissions themselves aren't stored anywhere - `POST /questions/{id}/submit`
grades synchronously and only this pass/fail outcome is persisted.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `user_id` | `uuid` | PK (1/2), -> `users(id)` on delete cascade | |
| `question_id` | `uuid` | PK (2/2), -> `questions(id)` on delete cascade | |
| `solved_at` | `timestamptz` | not null, default `now()` | |

`mark_solved()` in [`queries/progress.py`](./queries/progress.py) inserts
with `on conflict do nothing`, so one query both records the solve and tells
the route whether it was the first time (drives whether coins get paid out).

## `shop_items`

Catalog of purchasable cosmetics.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `name` | `text` | not null | |
| `price` | `integer` | not null, check `>= 0` | |
| `image_url` | `text` | not null, default `''` | Static asset path or external URL - no file storage service |

## `inventory`

What each user owns. Primary key stops buying the same item twice.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `user_id` | `uuid` | PK (1/2), -> `users(id)` on delete cascade | |
| `item_id` | `uuid` | PK (2/2), -> `shop_items(id)` on delete cascade | |
| `bought_at` | `timestamptz` | not null, default `now()` | |

---

## Relationships

- `sessions.user_id` -> `users.id`
- `test_cases.question_id` -> `questions.id`
- `completions.user_id` -> `users.id`
- `completions.question_id` -> `questions.id`
- `inventory.user_id` -> `users.id`
- `inventory.item_id` -> `shop_items.id`

## Indexes

- `sessions (user_id)`
- `test_cases (question_id)`
- `completions (user_id)`

---

## Deferred / not built yet

Ideas from an earlier draft of this doc that aren't in `schema.sql` and
nothing currently reads or writes. Listed here so the thinking isn't lost,
not as a spec to build against yet:

- **`is_admin`** flag on `users`, to gate question/shop authoring.
- **`tags`, `coin_reward`, `is_published`** columns on `questions`.
- **A submissions history table** - storing every code run (not just the
  latest pass/fail), for things like a submissions tab or plagiarism checks.
- **A `coin_transactions` ledger** - an audit trail instead of mutating
  `users.coins` directly.
- **Splitting `inventory`** into unique cosmetics vs. stackable resources.
  Note: an earlier draft described the stackable side as "seeds, plants,
  farm animals," which is a farming-game vocabulary that doesn't match this
  app's actual keycap/case shop - if this gets picked up, redesign it around
  what this shop really sells rather than reusing that language.

---

The full, authoritative SQL lives in [`schema.sql`](./schema.sql) - that's
what [`reset_db.py`](./reset_db.py) runs (along with `seed.sql` and
`load_questions.py`) to rebuild the database from scratch.

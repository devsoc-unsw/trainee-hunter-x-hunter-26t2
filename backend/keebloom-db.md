# Keebloom Database Schema

Postgres schema for this project's own database (the `database` service in
[`compose.yaml`](../compose.yaml)) - no external auth or storage service.
Authentication is handled directly by the FastAPI backend: passwords are
bcrypt-hashed and checked in [`security.py`](./security.py), and login
sessions are plain rows in the `sessions` table, not JWTs from a third-party
provider.

Schema is applied by running [`schema.sql`](./schema.sql) directly - that's
the source of truth; this doc is a readable summary of it. To change a table,
edit `schema.sql` and re-run `uv run python reset_db.py`, which drops and
rebuilds every table (see the root [README](../README.md) for the full
local-dev flow).

This describes what's actually in `schema.sql` right now - what the current
routers, queries, and tests are built against. See
[The farm - planned, not built](#the-farm---planned-not-built) at the bottom
for the decoration gameplay design, and
[Other deferred ideas](#other-deferred-ideas) for everything else that isn't
implemented.

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

## The farm - planned, not built

Keebloom's shop exists to decorate a **keyboard farm**. None of this section
is in `schema.sql`; it's a design to review and build in phases. The current
`seed.sql` items (Blue Keycaps, Cat Sticker, ...) are trainee-template
placeholders, not the real catalog.

### Phase 1 - cosmetics and placement

**Today's shop sells unique cosmetics only**: one per account, unlocked
permanently. Buying unlocks the item *type*, and you can then place unlimited
copies of it on your grid. That keeps `inventory` exactly as it is - no
quantities, and no reconciling "owned" against "placed".

```sql
-- shop_items gains one column
category text not null default 'farm' check (category in ('farm', 'keyboard'))

-- one new table
create table placements (
    user_id   uuid not null references users (id) on delete cascade,
    x         integer not null check (x >= 0),
    y         integer not null check (y >= 0),
    item_id   uuid not null,
    placed_at timestamptz not null default now(),
    primary key (user_id, x, y),
    foreign key (user_id, item_id) references inventory (user_id, item_id)
        on delete cascade
);
```

`primary key (user_id, x, y)` *is* the one-item-per-tile rule, and it's also
the only index this table needs - `where user_id = %s` is the sole read.

The composite foreign key makes "you can only place what you own" a database
guarantee rather than route code, and cascades a sold/removed item off the
farm automatically. It works only because `inventory`'s primary key is already
exactly `(user_id, item_id)` in that order - a strong reason not to
restructure `inventory` (see Phase 2).

Grid bounds belong in a new `farm.py` (`FARM_WIDTH`, `FARM_HEIGHT`), mirroring
how `keyboard.py` owns the unlock rules with the frontend just drawing what
it's told - **not** a check constraint, so resizing the farm isn't a data wipe.

New code this needs: `farm.py`, `queries/farm.py` (`list_placements`,
`place_item`, `clear_tile`), `routers/farm.py`, `Placement`/`PlaceRequest`
models, and the matching `types.ts` entries.

### Phase 2 - the farm shop (plantables, bought in quantity)

Planned: a second shop selling things you plant, purchasable in multiples,
possibly generating income. Not built - but Phase 1 is deliberately shaped so
this drops in cleanly.

**When it lands, add a quantity column to the existing `inventory` table
rather than splitting it into two:**

```sql
-- inventory gains one column
quantity integer not null default 1 check (quantity >= 0)
```

The primary key stays `(user_id, item_id)`, so `list_inventory` and
`owns_item` are untouched and - critically - Phase 1's `placements` foreign
key keeps working. Only `add_to_inventory` changes:

```sql
on conflict (user_id, item_id) do update set quantity = inventory.quantity + 1
```

The alternative (separate `cosmetic_inventory` and `resource_inventory`
tables) forces a UNION on every "what do I own" read, makes `owns_item` check
both tables, and makes the buy path fetch the item type and branch before it
can write - two near-identical tables and double the query surface for the
same result.

Knock-on effects to expect:

- `ShopItem.owned: bool` stops being enough for stackables; that model and
  `types.ts` need a quantity for farm-shop items.
- The "already owned -> 409" rule in `routers/shop.py` (and
  `test_cannot_buy_twice`) applies to unique cosmetics only - the buy route
  will branch by category.
- `category`'s check constraint extends by one line. Worth deciding properly
  at that point: `category` currently means *where an item is used* (farm grid
  vs keyboard), whereas plantable-vs-unique is a different axis. That may want
  a third category value or a separate `stackable` boolean.

### Phase 3 - growth and plant income (idea only)

If plants generate coins, that's a **second coin faucet** to balance against
`rewards.py` - it needs a deliberate design pass, not a drive-by.

If growth ships, the minimal shape is one nullable column on `placements`
(`planted_at_solves integer`) plus a pure `growth_stage()` function in
`farm.py`. Drive it off the user's solve count, not wall-clock time: that
stays deterministic, unit-testable with no database (like
`tests/unit/test_keyboard.py`), needs no scheduler, and reinforces the core
loop instead of rewarding idling.

### Considered and dropped

| Idea | Why not |
|---|---|
| `is_equipped` on inventory | Needs a partial unique index to stop two keycap sets being equipped at once. Nullable `equipped_keycaps_id` / `equipped_case_id` FK slots on `users` get "exactly one equipped" for free. |
| `shop_items.is_active` | While `reset_db.py` wipes everything, deleting the row from `seed.sql` does the same job. Revisit at launch. |
| `shop_items.created_at` | Nothing sorts by it; `list_items` orders by `price, name`. |
| Five-value `item_type` (decoration/building/seed/plant/animal) | Implies five mechanics that don't exist. Two-value `category` now; extend the check constraint the day a mechanic does. |

### Build sequencing, when Phase 1 starts

1. `routers/shop.py` and `rewards.py` must work first. Until buying works,
   `inventory` is always empty, so the placement foreign key means nothing can
   be placed.
2. Add `drop table if exists placements cascade;` at the **top** of
   `schema.sql`, before the `inventory` drop - otherwise the second
   `reset_db.py` run fails on "relation already exists", and so does the second
   `pytest` session (`conftest.py` reuses a persistent `trainee_hunter_test`
   database).
3. Create `placements` **last**, after `inventory`, because of the composite
   foreign key. Creates are order-sensitive even though cascading drops aren't.
4. Keep `seed.sql` at 4+ items with at least one under 1000 coins, or
   `tests/api/test_shop.py` breaks (`test_shop_lists_items` asserts >= 4,
   `test_coins_never_go_negative` buys the whole catalog with 1000 coins).

## Other deferred ideas

Not farm-related, nothing reads or writes these:

- **`is_admin`** flag on `users`, to gate question/shop authoring.
- **`tags`, `coin_reward`, `is_published`** columns on `questions`.
- **A submissions history table** - storing every code run (not just the
  latest pass/fail), for a submissions tab or plagiarism checks.
- **A `coin_transactions` ledger** - an audit trail instead of mutating
  `users.coins` directly.

---

The full, authoritative SQL lives in [`schema.sql`](./schema.sql) - that's
what [`reset_db.py`](./reset_db.py) runs (along with `seed.sql` and
`load_questions.py`) to rebuild the database from scratch.

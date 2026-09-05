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
[Still to build](#still-to-build) at the bottom for the parts of the
decoration gameplay the database is ready for but no route serves yet, and
[Other deferred ideas](#other-deferred-ideas) for everything else.

## Overview

| Table | Purpose |
|---|---|
| [`users`](#users) | Account data - username, password hash, coin balance, keys bought |
| [`sessions`](#sessions) | Login tokens, one row per logged-in device |
| [`questions`](#questions) | Coding problems |
| [`test_cases`](#test_cases) | Grading inputs/outputs for each question |
| [`completions`](#completions) | Which user solved which question |
| [`shop_items`](#shop_items) | Catalog of purchasable cosmetics |
| [`inventory`](#inventory) | What each user has bought, and how many |
| [`key_unlocks`](#key_unlocks) | Which keys a user has unlocked |
| [`key_decor`](#key_decor) | How each key on a user's keyboard is dressed |
| [`key_presses`](#key_presses) | Per-user, per-key typing counts |

### The keyboard farm, in one paragraph

Keebloom's shop decorates a **keyboard farm**. Solving a problem or buying an
`extra-key` earns an unlock **credit**; you spend one by clicking any locked
key, and that key becomes yours (`key_unlocks`). Skins and accessories are
bought **in quantities** - one copy dresses one key - so `inventory` says how
many you own and `key_decor` says where they are. Taking an item off a key
makes it placeable again, with no refund step anywhere: how many are placed is
*counted* off `key_decor` rather than stored, so the two numbers can't drift.
Fish and jellyfish only go on water keys; flowers and vegetables only on the
rest. That last rule is the one thing here the database can't enforce itself -
see [`decor.py`](./decor.py).

### The three numbers that make an item work

Only one of them is stored:

```
quantity   inventory.quantity            how many you bought      (a column)
placed     count(*) over key_decor       how many are on a key    (derived)
available  quantity - placed             how many you can plant   (a subtraction)
```

`queries.shop.units_available` is the one function that does this, and every
placement route calls it. See [`inventory`](#inventory) for why `placed` isn't
a column.

---

## `users`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `username` | `text` | not null, unique | |
| `password_hash` | `text` | not null | bcrypt hash, set/checked in [`security.py`](./security.py) |
| `coins` | `integer` | not null, default `0`, check `>= 0` | In-game currency balance, mutated in place (no ledger) |
| `keys_bought` | `integer` | not null, default `0`, check `>= 0` | Keys unlocked **with coins**. Not the total - see below |
| `created_at` | `timestamptz` | not null, default `now()` | |

`POST /auth/signup` ([`routers/auth.py`](./routers/auth.py)) is the only
thing that creates a row here.

`keys_bought` deliberately stores only what was *purchased*, not how many keys
are unlocked in total. [`keyboard.py`](./keyboard.py) adds `STARTING_KEYS` and
the solve count on top and caps at `len(KEY_UNLOCK_ORDER)`, so those numbers
live in one place instead of being half-duplicated as a SQL `default 4`. The
database stores the progress, Python owns the rules.

That total is an **allowance**, not a state: it says how many keys the user has
earned the right to unlock. Which ones they actually picked is
[`key_unlocks`](#key_unlocks), and the difference between the two is how many
credits they have left to spend.

`buy_key_unlock()` in [`queries/users.py`](./queries/users.py) is the only
thing that increments it, and it puts both guards in the `WHERE` clause the way
`spend_coins` does - the balance can't go negative and the count can't run past
the end of the keyboard, even under concurrent requests.

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

Catalog of purchasable cosmetics. Skins and accessories are bought **in
quantities** - one copy dresses one key, and buying the same thing again stacks
rather than 409ing. `kind = 'key_unlock'` is the exception: it never reaches
`inventory` at all, it increments `users.keys_bought` instead.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `slug` | `text` | not null, unique | Stable name, eg `blue-tulip`. What the frontend keys its drawings off, and what makes `seed.sql` re-runnable |
| `name` | `text` | not null | Display name |
| `price` | `integer` | not null, check `>= 0` | But see the seeding rules below - nothing may actually be free |
| `image_url` | `text` | not null, default `''` | Which drawing this is, relative to `frontend/src/assets/`. Documentation, not a usable `src` |
| `kind` | `text` | not null, check ∈ `key_skin`/`accessory` | A skin recolours a key; an accessory sits on one |
| `habitat` | `text` | not null, check ∈ `land`/`water` | An accessory only goes on a key of the same habitat |

**Why `slug` rather than just using `image_url` as an image source:** Vite
content-hashes everything under `src/assets/`, so the built filename isn't
knowable from the database. The frontend maps `slug` -> an `import`ed asset.
`slug` also gives `seed.sql` something to `on conflict` on, which makes it
safe to re-run standalone - you can add items or reprice the catalog **without
`reset_db.py` wiping every account**, and item ids stay stable so nobody's
inventory breaks. It's the closest thing this repo has to a migration.

**Why `habitat` is one column and not a compatibility table:** the whole rule
is "fish on water keys, everything else on land keys", so it reduces to
`accessory.habitat = skin.habitat`. Soil and grass are both `land`.

### Seeding rules that `tests/api/test_shop.py` silently depends on

1. **Nothing is free.** `test_cannot_buy_what_you_cannot_afford` gives a user 0
   coins and expects a 402 on the cheapest item - a price of 0 would sell it to
   them and fail the test. This is why grass, the default key, isn't sold at
   all: a key with no skin renders grass already, so reverting is free without
   needing a price-0 row.
2. **At least 4 items, catalog affordable on 1000 coins.**
   `test_shop_lists_items` asserts `>= 4`; `test_coins_never_go_negative` buys
   the lot. The current catalog is 13 items totalling 193.

Prices are **per placement** now, so they're roughly a quarter of what they
were when one purchase decorated the whole keyboard. Because `seed.sql` upserts
on `slug`, rebalancing is just re-running it - no `reset_db.py`, no wiped
accounts, and nobody's existing quantities move.

## `inventory`

How many of each item a user has bought. One row per `(user, item)` no matter
how many copies.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `user_id` | `uuid` | PK (1/2), -> `users(id)` on delete cascade | |
| `item_id` | `uuid` | PK (2/2), -> `shop_items(id)` on delete cascade | |
| `quantity` | `integer` | not null, default `1`, check `>= 0` | How many were **bought**. Not how many are free to place |
| `bought_at` | `timestamptz` | not null, default `now()` | |

That the primary key is exactly `(user_id, item_id)` **in that order** is load
bearing - it's what lets `key_decor` point a composite foreign key at it. The
quantity is a column rather than one row per copy for the same reason: the
foreign key needs exactly one row to reference.

**Why there's no `placed` column.** How many copies are currently on a key is
already recorded - it's the number of `key_decor` rows pointing at the item -
so storing it too would be two numbers that must agree, kept in sync by hand
across four different write paths (place, replace, evict-on-skin-change,
clear-key). Counting it instead means **nothing in this codebase refunds an
item**: taking a flower off a key makes it available again by definition, and
no missed code path can leak or duplicate a copy.

`queries.shop.units_available` is the one place that does the subtraction. It
opens with `select quantity ... for update`, which locks the user's inventory
row for the rest of the request. Without that lock, two placements arriving
together both read `placed = 0`, both see the last copy as free, and both
write - the count subquery alone can't stop it, because they touch *different*
`key_decor` rows and postgres has nothing to serialise on.

**Never delete a row here when `quantity` hits 0.** `key_decor`'s composite
foreign keys are `on delete cascade`, so dropping an inventory row wipes the
whole `key_decor` row - including the *other* slot. `check (quantity >= 0)`
rather than a delete is what keeps that from happening.

## `key_unlocks`

Which keys a user has unlocked. One row per key, written when they spend an
unlock credit on it.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `user_id` | `uuid` | PK (1/2), -> `users(id)` on delete cascade | |
| `key_char` | `text` | PK (2/2), check `char_length = 1` | The key itself, eg `f`. Lowercase |
| `unlocked_at` | `timestamptz` | not null, default `now()` | |

Two halves of one rule, deliberately split:

```
allowance = STARTING_KEYS + solves + users.keys_bought   keyboard.unlock_allowance()
spent     = count(*) from key_unlocks                    this table
credits   = allowance - spent                            routers/users.py
```

`keyboard.py` owns the arithmetic and this table owns the choices, so neither
can answer the other's question. `queries.keys.unlock_key` puts the guard in
the `WHERE` clause the way `spend_coins` does - the insert produces a row only
while `count(*) < allowance`, so two requests can't both spend the last credit.

`queries.users.create_user` grants `keyboard.STARTING_KEY_CHARS` here on
signup. That's in the query rather than the signup route on purpose: a user
with no rows in this table can't decorate anything at all (see the foreign key
below), so every path that makes a user has to make them a keyboard too.

This table replaces a design decision that used to be in
[Considered and dropped](#considered-and-dropped): "the unlock ORDER is fixed,
so a single count says everything a table of rows would". That was true right
up until the user got to pick which key, which is exactly what a count can't
express.

## `key_decor`

How one user has dressed one key. No row - or a null slot - means the default:
a grass key with nothing on it, which is what `Keyboard.tsx` already draws.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `user_id` | `uuid` | PK (1/2), -> `users(id)` on delete cascade | |
| `key_char` | `text` | PK (2/2), check `char_length = 1` | The key itself, eg `f`. Lowercase |
| `skin_id` | `uuid` | nullable, composite FK (see below) | Null = the default grass |
| `accessory_id` | `uuid` | nullable, composite FK (see below) | Null = nothing on this key |
| `updated_at` | `timestamptz` | not null, default `now()` | |

Four things here are doing more work than they look:

- **`primary key (user_id, key_char)` *is* the one-skin-one-accessory-per-key
  rule.** Placing a second flower on the same key updates the row instead of
  adding one. It's also the only index the table needs - `where user_id = %s`
  is the only way anything reads it.
- **The composite foreign keys `(user_id, skin_id)` and `(user_id, accessory_id)`
  -> `inventory (user_id, item_id)` make "you can only place what you own" a
  database guarantee**, not route code that could be forgotten. Verified by
  `test_cannot_place_an_item_you_do_not_own`, which asserts a raw
  `ForeignKeyViolation`. Note this is *ownership*, not stock - **how many**
  copies you may place is `units_available`, because a foreign key can only
  ask "does the row exist", not "are there any spare".
- **`(user_id, key_char)` -> `key_unlocks` makes "you can't decorate a locked
  key" the same kind of guarantee.** It works for the same reason the two
  above do: `key_unlocks`' primary key is already exactly `(user_id, key_char)`
  in that order. `routers/decor.py` still checks it first, so the user gets a
  403 rather than the 500 a raw constraint violation would produce.
- **The slots are nullable on purpose.** Postgres foreign keys default to
  `MATCH SIMPLE`, which skips the check entirely when any column of the key is
  null - so an empty slot is legal with no extra machinery.

This table is also, incidentally, the stock ledger: every row referencing an
item is one copy of it in use. That's what `units_available` counts, and why
`clear_key` deleting a row *is* the refund.

Both item slots live in one row rather than in two tables so that drawing a
whole keyboard is a single `select`.

**Caveat if item-selling ever ships:** `on delete cascade` on those composite
FKs means deleting an `inventory` row drops the whole `key_decor` row -
including the *other* slot. Nothing deletes inventory rows today. When
something does, switch to `on delete set null (skin_id)`, which needs Postgres
15+ (`compose.yaml` pins `postgres:17-alpine`, so that's fine).

**What this table can't enforce:** that a fish is on a water key. A check
constraint only sees the row it's on, and the accessory's habitat and the
skin's habitat are two different `shop_items` rows. A trigger could reach
across, but nothing else in this codebase uses triggers, so the rule lives in
[`decor.py`](./decor.py) as a pure function instead - unit-testable with no
database, exactly like `keyboard.py`.

The related hole: change a water key to soil and its fish is suddenly on dry
land, and no constraint catches it. `set_skin()` in
[`queries/decor.py`](./queries/decor.py) takes a `keep_accessory` bool that the
route computes (it has already read the skin to check ownership, so it knows
both habitats) and clears the accessory in the same statement that moves the
key.

## `key_presses`

Typing counts for the keyboard minigame, one row per user per key. Feeds the
count badge `Key.tsx` draws and the `pressCounts` prop `Keyboard.tsx` takes.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `user_id` | `uuid` | PK (1/2), -> `users(id)` on delete cascade | |
| `key_char` | `text` | PK (2/2), check `char_length = 1` | |
| `presses` | `integer` | not null, default `0`, check `>= 0` | |

This replaces the module-level `dict` `routers/keylogger.py` started with,
which counted **every user** into one shared counter and lost it on restart.

`record_press()` in [`queries/keypresses.py`](./queries/keypresses.py) does
insert-or-increment in one statement and `returning presses` hands back the new
total in the same round trip - so a payout rule like "a coin every 10 presses"
is just `presses % 10 == 0`, with no extra column and no read-then-write race.

Neither this table nor `key_decor` constrains `key_char` against the real key
list - that would copy `KEY_UNLOCK_ORDER` into SQL. Python owns the key list;
the length check is only a sanity guard.

---

## Relationships

- `sessions.user_id` -> `users.id`
- `test_cases.question_id` -> `questions.id`
- `completions.user_id` -> `users.id`
- `completions.question_id` -> `questions.id`
- `inventory.user_id` -> `users.id`
- `inventory.item_id` -> `shop_items.id`
- `key_unlocks.user_id` -> `users.id`
- `key_decor.user_id` -> `users.id`
- `key_decor (user_id, key_char)` -> `key_unlocks (user_id, key_char)`
- `key_decor (user_id, skin_id)` -> `inventory (user_id, item_id)`
- `key_decor (user_id, accessory_id)` -> `inventory (user_id, item_id)`
- `key_presses.user_id` -> `users.id`

## Indexes

- `sessions (user_id)`
- `test_cases (question_id)`
- `completions (user_id)`

`key_decor`, `key_unlocks` and `key_presses` need none beyond their primary
keys - all three are only ever read `where user_id = %s`, which the PK already
covers as a prefix. `units_available`'s count over `key_decor` is the one query
that filters on an item rather than a key, and it's still `where user_id = %s`
first, so the same prefix serves it.

---

## Still to build

The database and every route over it are done. What's listed here is what a
future feature would touch, not missing work.

### Selling items back

Nothing deletes an `inventory` row today, and nothing should start without
reading the caveat under [`key_decor`](#key_decor) first: the composite foreign
keys are `on delete cascade`, so removing an inventory row takes the whole
`key_decor` row with it, including the *other* slot. A sell route wants
`on delete set null (skin_id)` (Postgres 15+, and `compose.yaml` pins 17) - or,
more simply, to decrement `quantity` and refuse to go below `placed`.

### An escalating key price

`extra-key` is a flat 50. `price_for_next_key(keys_bought)` drops in later as a
pure function in `keyboard.py` with no schema change - `users.keys_bought` is
already the input it needs.

### Growth and plant income (idea only)

If plants generate coins, that's a **second coin faucet** to balance against
`rewards.py` - and now a third, since keypresses pay out too. It needs a
deliberate design pass, not a drive-by.

If growth ships, the minimal shape is one nullable column on `key_decor`
(`planted_at_solves integer`) plus a pure `growth_stage()` function in
`decor.py`. Drive it off the user's solve count, not wall-clock time: that
stays deterministic, unit-testable with no database, needs no scheduler, and
reinforces the core loop instead of rewarding idling.

### Considered and dropped

| Idea | Why not |
|---|---|
| An `(x, y)` farm grid (`placements`) | This was the original Phase 1 design. The frontend decorates *keys*, not a canvas - `key_decor` is the same idea with `key_char` where `(x, y)` was. |
| A check constraint for the fish-needs-water rule | Postgres check constraints can't reference another table, and this codebase has no triggers. Lives in `decor.py`. |
| Denormalising habitat into `key_decor` so a constraint *could* check it | Two copies of a value that already lives in `shop_items`, kept in sync by hand, to save one Python comparison. |
| Selling grass as a price-0 item | A free item breaks `test_cannot_buy_what_you_cannot_afford`. A key with no skin already renders grass, so the default costs nothing to return to. |
| `is_equipped` on inventory | Needs a partial unique index to stop two skins being equipped at once. `key_decor`'s primary key gets "one per key" for free. |
| ~~A `key_unlocks` table listing which keys a user owns~~ | **Reversed - it shipped.** The reason given was "the unlock ORDER is fixed, so a single count says everything a table of rows would". Letting the user choose which key removed that premise: a count can say *how many*, never *which*. See [`key_unlocks`](#key_unlocks). |
| A `placed` counter on `inventory` | It's already recorded - one `key_decor` row per copy in use. Two numbers that must agree, maintained across four write paths, to save a `count(*)`. Counting it instead is what makes "taking an item off a key frees it" true with no refund code at all. |
| A `quantity` on `key_decor` (several flowers on one key) | The primary key is `(user_id, key_char)` precisely so a key wears one skin and one accessory. Stacking belongs in `inventory`, not here. |
| `shop_items.is_active` | Deleting the row from `seed.sql` does the same job. Revisit at launch. |
| `shop_items.created_at` | Nothing sorts by it; `list_items` orders by `price, name`. |

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

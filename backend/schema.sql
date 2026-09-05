-- full schema for the app. reset_db.py drops everything and runs this file.
-- if you change a table here, re-run reset_db.py (it wipes all data).

-- decor and presses drop first: key_decor has composite foreign keys into both
-- inventory and key_unlocks, so it has to go before the tables it points at.
drop table if exists key_decor cascade;
drop table if exists key_presses cascade;
drop table if exists key_unlocks cascade;
drop table if exists inventory cascade;
drop table if exists shop_items cascade;
drop table if exists completions cascade;
drop table if exists test_cases cascade;
drop table if exists questions cascade;
drop table if exists sessions cascade;
drop table if exists users cascade;

create table users (
    id            uuid primary key default gen_random_uuid(),
    username      text not null unique,
    password_hash text not null,
    coins         integer not null default 0 check (coins >= 0),
    -- keys BOUGHT with coins, not the total unlocked. keyboard.py owns
    -- STARTING_KEYS and adds it on top, so the starting number lives in one
    -- place instead of being duplicated as a default here.
    keys_bought   integer not null default 0 check (keys_bought >= 0),
    created_at    timestamptz not null default now()
);

-- one row per logged in device. logging out deletes the row.
create table sessions (
    token      text primary key,
    user_id    uuid not null references users (id) on delete cascade,
    created_at timestamptz not null default now()
);

create table questions (
    id            uuid primary key default gen_random_uuid(),
    -- human readable id from questions.csv, eg 'two-sum'. links the two csvs.
    slug          text not null unique,
    name          text not null,
    details       text not null,
    difficulty    text not null check (difficulty in ('easy', 'medium', 'hard')),
    -- the function the user has to write, eg 'two_sum'
    function_name text not null,
    -- what we prefill the editor with
    starter_code  text not null default ''
);

-- input is the argument list, expected is the return value.
-- eg two_sum([2,7,11,15], 9) -> [0,1] is input '[[2,7,11,15], 9]', expected '[0,1]'
create table test_cases (
    id          uuid primary key default gen_random_uuid(),
    question_id uuid not null references questions (id) on delete cascade,
    input       jsonb not null,
    expected    jsonb not null,
    -- samples are shown on the question page, the rest are hidden
    is_sample   boolean not null default false
);

-- one row per question a user has solved. no row = not solved yet.
create table completions (
    user_id     uuid not null references users (id) on delete cascade,
    question_id uuid not null references questions (id) on delete cascade,
    solved_at   timestamptz not null default now(),
    primary key (user_id, question_id)
);

create table shop_items (
    id        uuid primary key default gen_random_uuid(),
    -- stable name for one item, eg 'blue-tulip'. the frontend maps this to an
    -- imported png (vite content-hashes src/assets, so a path string here
    -- could never resolve), and it lets seed.sql re-run without duplicating.
    slug      text not null unique,
    name      text not null,
    price     integer not null check (price >= 0),
    image_url text not null default '',
    -- what the item is for: a skin recolours a key, an accessory sits on one
    kind      text not null check (kind in ('key_skin', 'accessory', 'key_unlock')),
    -- fish go on water keys, flowers go on land ones. this makes that rule
    -- 'accessory.habitat = skin.habitat' instead of a special case per item.
    habitat   text not null check (habitat in ('land', 'water'))
);

-- what each user owns, and how many of it. one row per (user, item) no matter
-- how many copies - the quantity is a column, not extra rows, so key_decor's
-- composite foreign key below still has something stable to point at.
--
-- NEVER delete a row here when quantity hits 0. key_decor's foreign keys are
-- 'on delete cascade', so dropping an inventory row wipes the whole key_decor
-- row - including the OTHER slot. a row sitting at quantity 0 is what keeps
-- that from happening.
create table inventory (
    user_id   uuid not null references users (id) on delete cascade,
    item_id   uuid not null references shop_items (id) on delete cascade,
    -- how many the user has BOUGHT. how many are currently placed is counted
    -- off key_decor instead of stored, so the two can never disagree and
    -- taking an item off a key frees it with no refund code anywhere.
    quantity  integer not null default 1 check (quantity >= 0),
    bought_at timestamptz not null default now(),
    primary key (user_id, item_id)
);

-- which keys a user has unlocked. one row per key, inserted when they spend an
-- unlock credit on it - so WHICH keys is a choice, not a prefix of a fixed
-- order. queries.users.create_user seeds the starting keys for every account.
--
-- how many unlocks a user has EARNED is still arithmetic (keyboard.py's
-- unlock_allowance, off solves and users.keys_bought); this table is what they
-- spent them on. credits left = allowance - count(*) here.
create table key_unlocks (
    user_id     uuid not null references users (id) on delete cascade,
    key_char    text not null check (char_length(key_char) = 1),
    unlocked_at timestamptz not null default now(),
    primary key (user_id, key_char)
);

-- how one user has dressed up one key. no row (or a null slot) = the default:
-- a grass key with nothing on it, which is what Keyboard.tsx already draws.
--
-- must be created AFTER inventory and key_unlocks because of the composite
-- foreign keys.
create table key_decor (
    user_id      uuid not null references users (id) on delete cascade,
    key_char     text not null check (char_length(key_char) = 1),
    skin_id      uuid,
    accessory_id uuid,
    updated_at   timestamptz not null default now(),
    -- one skin and one accessory per key, enforced by the key itself. it's
    -- also the only index this table needs - 'where user_id = %s' is the
    -- only way anything reads it.
    primary key (user_id, key_char),
    -- 'you can only decorate a key you've unlocked', as a database guarantee.
    -- same trick as the two below: key_unlocks' primary key is already exactly
    -- (user_id, key_char) in that order.
    foreign key (user_id, key_char) references key_unlocks (user_id, key_char) on delete cascade,
    -- 'you can only place what you own', as a database guarantee rather than
    -- route code. works because inventory's primary key is already exactly
    -- (user_id, item_id) in that order.
    --
    -- HOW MANY you can place is not here: it's quantity minus the number of
    -- rows in this table pointing at the item, which a check constraint can't
    -- see. that guard lives in queries.shop.units_available.
    --
    -- the slots are nullable on purpose: postgres foreign keys default to
    -- MATCH SIMPLE, which skips the check entirely when any column of the
    -- key is null. so an empty slot needs no extra machinery.
    foreign key (user_id, skin_id)      references inventory (user_id, item_id) on delete cascade,
    foreign key (user_id, accessory_id) references inventory (user_id, item_id) on delete cascade
);

-- keypress counts for the keyboard minigame, one row per user per key.
-- replaces the in-memory dict routers/keylogger.py started with, which was
-- shared across every user and lost on restart.
create table key_presses (
    user_id  uuid not null references users (id) on delete cascade,
    key_char text not null check (char_length(key_char) = 1),
    presses  integer not null default 0 check (presses >= 0),
    primary key (user_id, key_char)
);

create index sessions_user_id_idx on sessions (user_id);
create index test_cases_question_id_idx on test_cases (question_id);
create index completions_user_id_idx on completions (user_id);

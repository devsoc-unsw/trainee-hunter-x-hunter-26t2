-- full schema for the app. reset_db.py drops everything and runs this file.
-- if you change a table here, re-run reset_db.py (it wipes all data).

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
    name      text not null,
    price     integer not null check (price >= 0),
    image_url text not null default ''
);

-- what each user owns. primary key stops you buying the same thing twice.
create table inventory (
    user_id   uuid not null references users (id) on delete cascade,
    item_id   uuid not null references shop_items (id) on delete cascade,
    bought_at timestamptz not null default now(),
    primary key (user_id, item_id)
);

create index sessions_user_id_idx on sessions (user_id);
create index test_cases_question_id_idx on test_cases (question_id);
create index completions_user_id_idx on completions (user_id);

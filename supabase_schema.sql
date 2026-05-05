-- Good to hear the name — Supabase schema
-- Run this in your Supabase project: SQL Editor → paste → Run

-- One table: every game result is a row
create table if not exists public.scores (
  id            bigint generated always as identity primary key,
  display_name  text   not null check (length(trim(display_name)) between 1 and 30),
  device_id     text   not null,                                -- anonymous device ID (random uuid in localStorage)
  player_id     text   not null,                                -- e.g. 'wes_morgan'
  day_index     int    not null,                                -- days since unix epoch, e.g. 20578
  attempts      int    null check (attempts is null or attempts between 1 and 5),
  correct       boolean not null,
  created_at    timestamptz default now()
);

-- One result per device per day (so people can't farm wins)
create unique index if not exists scores_device_day_uq
  on public.scores (device_id, day_index);

-- Useful indexes
create index if not exists scores_day_idx        on public.scores (day_index);
create index if not exists scores_name_day_idx   on public.scores (display_name, day_index);

-- Row Level Security: anyone can read, anyone can insert their own row
alter table public.scores enable row level security;

drop policy if exists scores_read on public.scores;
create policy scores_read on public.scores
  for select using (true);

drop policy if exists scores_insert on public.scores;
create policy scores_insert on public.scores
  for insert with check (
    length(trim(display_name)) between 1 and 30
    and length(device_id) between 8 and 64
  );

-- (No update / delete policies = nobody can change scores after submission.)

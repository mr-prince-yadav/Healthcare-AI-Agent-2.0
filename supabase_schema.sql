-- Enable UUID extension (for primary keys)
create extension if not exists "pgcrypto";

-- 1. Profiles table
create table if not exists profiles (
    user_id uuid primary key,               -- Supabase Auth user id
    data jsonb not null default '{}'::jsonb, -- All profile, health, medications, appointments stored here
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Trigger to automatically update updated_at
create or replace function update_profiles_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger set_updated_at
before update on profiles
for each row
execute function update_profiles_updated_at();

-- 2. Optional: Add indexes to query JSON fields faster
-- Example: index for email inside JSON data
create index if not exists idx_profiles_email on profiles ((data->>'email'));

-- Example: index for medications array inside JSON (for searching)
create index if not exists idx_profiles_medications on profiles using gin ((data->'medication_list'));

-- 3. Optional: For full-text search on disease or other medical info
create index if not exists idx_profiles_disease on profiles using gin (to_tsvector('english', data->>'disease'));

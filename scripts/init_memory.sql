-- Memu Memory Initialization
-- This script creates the tables required for the Intelligence Service.
-- It is designed to be run against the database used by the Intelligence Service.

-- 1. Household Memory (Facts)
CREATE TABLE IF NOT EXISTS household_memory (
    id SERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    fact TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at BIGINT NOT NULL -- Timestamp in milliseconds
);

CREATE INDEX IF NOT EXISTS idx_memory_room ON household_memory(room_id);
CREATE INDEX IF NOT EXISTS idx_memory_fact ON household_memory(fact);

-- 2. Shared Lists (Shopping, Todo)
CREATE TABLE IF NOT EXISTS shared_lists (
    id SERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    item TEXT NOT NULL,
    added_by TEXT NOT NULL,
    added_at BIGINT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lists_room ON shared_lists(room_id);

-- 3. Reminders
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    due_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_reminders_due_processed ON reminders(due_at, processed);

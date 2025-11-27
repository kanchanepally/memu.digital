CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    due_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

-- Index for faster polling
CREATE INDEX IF NOT EXISTS idx_reminders_due_processed ON reminders(due_at, processed);

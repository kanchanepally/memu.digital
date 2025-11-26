-- Connect to the immich database (where Synapse lives)
-- This script is intended to be run against the 'immich' database

-- 1. Create the AI tables (Memory & Lists)
CREATE TABLE IF NOT EXISTS household_memory (
    id SERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    fact TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS shared_lists (
    id SERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    item TEXT NOT NULL,
    added_by TEXT NOT NULL,
    added_at BIGINT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP
);

-- 2. Create a "processed_by_ai" column tracker
-- Since we can't easily modify Synapse's tables, we'll use a separate table to track progress
CREATE TABLE IF NOT EXISTS ai_processed_events (
    event_id TEXT PRIMARY KEY
);

-- 3. Create the "messages" VIEW to bridge Synapse -> AI
-- This pulls text messages from Synapse's event tables
CREATE OR REPLACE VIEW messages AS
SELECT 
    e.event_id AS id,
    e.room_id,
    e.sender,
    ej.json::json->'content'->>'body' AS content,
    e.origin_server_ts AS timestamp,
    (EXISTS (SELECT 1 FROM ai_processed_events ape WHERE ape.event_id = e.event_id)) AS processed_by_ai
FROM events e
JOIN event_json ej ON e.event_id = ej.event_id
WHERE e.type = 'm.room.message' 
  AND ej.json::json->'content'->>'msgtype' = 'm.text';

-- 4. Create a function to handle the "UPDATE messages SET processed_by_ai = true"
-- The AI tries to update the view, so we need a trigger to redirect that update
CREATE OR REPLACE FUNCTION mark_message_processed() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.processed_by_ai = true THEN
        INSERT INTO ai_processed_events (event_id) VALUES (OLD.id)
        ON CONFLICT (event_id) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER ai_message_processed_trigger
INSTEAD OF UPDATE ON messages
FOR EACH ROW
EXECUTE FUNCTION mark_message_processed();

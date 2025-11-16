CREATE TABLE IF NOT EXISTS households (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID REFERENCES households(id),
    matrix_user_id VARCHAR(255) UNIQUE,
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shared_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID,
    category VARCHAR(50) DEFAULT 'general',
    task VARCHAR(500) NOT NULL,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    completed_by VARCHAR(255)
);

CREATE INDEX idx_tasks ON shared_tasks(household_id, category, completed);

CREATE TABLE IF NOT EXISTS household_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id VARCHAR(255) NOT NULL,
    fact TEXT NOT NULL,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id VARCHAR(255) NOT NULL,
    sender VARCHAR(255) NOT NULL,
    content TEXT,
    timestamp TIMESTAMP NOT NULL,
    processed_by_ai BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS shared_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id VARCHAR(255) NOT NULL,
    item VARCHAR(255) NOT NULL,
    added_by VARCHAR(255),
    added_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP
);

INSERT INTO households (name) VALUES ('My Household');

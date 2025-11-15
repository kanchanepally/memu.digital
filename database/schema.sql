-- Hearth OS Database Schema

-- TODO: Copy complete schema from artifact
-- "Hearth Family - Simple Database Schema"

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matrix_user_id VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add more tables from artifact...

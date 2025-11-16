-- Hearth Family Database
-- Simple schema for: Messages (Matrix), Photos, Tasks

-- Family Members
CREATE TABLE family_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matrix_user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Photos
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    caption TEXT,
    uploaded_by UUID REFERENCES family_members(id),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    tags TEXT[]
);

-- Tasks (with AI categories)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    -- Categories: shopping, housework, errands, kids, garden, other
    notes TEXT,
    created_by UUID REFERENCES family_members(id),
    created_at TIMESTAMP DEFAULT NOW(),
    due_date DATE,
    completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    completed_by UUID REFERENCES family_members(id)
);

-- Memories (AI-powered recall)
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    category VARCHAR(50),
    -- Categories: passwords, important-dates, health, home, financial, other
    created_by UUID REFERENCES family_members(id),
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP
);

-- Plans (Future events, trips, etc.)
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    plan_date DATE,
    created_by UUID REFERENCES family_members(id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT false
);

-- Indexes for performance
CREATE INDEX idx_photos_uploaded ON photos(uploaded_at DESC);
CREATE INDEX idx_tasks_category ON tasks(category, completed);
CREATE INDEX idx_tasks_due ON tasks(due_date) WHERE completed = false;
CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_plans_date ON plans(plan_date) WHERE completed = false;

-- Sample data
INSERT INTO family_members (matrix_user_id, name) 
VALUES ('@demo:family.hearth.local', 'Demo User');
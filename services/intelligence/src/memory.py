import logging
import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import Config

logger = logging.getLogger("memu.memory")

class MemoryStore:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Establish database connection pool."""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    host=Config.DB_HOST,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD
                )
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
                raise

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def init_db(self):
        """Initialize database tables if they don't exist."""
        sql = """
        -- 1. Household Memory (Facts)
        CREATE TABLE IF NOT EXISTS household_memory (
            id SERIAL PRIMARY KEY,
            room_id TEXT NOT NULL,
            fact TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at BIGINT NOT NULL
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
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(sql)
            logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def add_reminder(self, room_id: str, user_id: str, content: str, due_at: datetime):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO reminders (room_id, user_id, content, due_at)
                VALUES ($1, $2, $3, $4)
            """, room_id, user_id, content, due_at)

    async def get_due_reminders(self) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, room_id, user_id, content
                FROM reminders
                WHERE due_at <= NOW() AND processed = FALSE
            """)
            return [dict(r) for r in rows]

    async def mark_reminder_processed(self, reminder_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE reminders SET processed = TRUE WHERE id = $1", reminder_id)

    async def remember_fact(self, room_id: str, sender: str, fact: str):
        async with self.pool.acquire() as conn:
            # Note: timestamp is bigint in the original schema (setup_ai_bridge.sql)
            # but usually it's better to be timestamp. I will stick to original schema compatibility if possible
            # or update it. The original `setup_ai_bridge.sql` used BIGINT for created_at.
            # I will assume we can use current timestamp or pass it.
            # Let's check schema again. `created_at BIGINT`.
            ts = int(datetime.now().timestamp() * 1000)
            await conn.execute("""
                INSERT INTO household_memory (room_id, fact, created_by, created_at)
                VALUES ($1, $2, $3, $4)
            """, room_id, fact, sender, ts)

    async def recall_facts(self, room_id: str, query: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT fact, created_at, created_by
                FROM household_memory
                WHERE room_id = $1
                AND fact ILIKE $2
                ORDER BY created_at DESC
                LIMIT 5
            """, room_id, f'%{query}%')
            return [dict(r) for r in rows]

    async def add_to_list(self, room_id: str, sender: str, items: List[str]):
        ts = int(datetime.now().timestamp() * 1000)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for item in items:
                    if item.strip():
                        await conn.execute("""
                            INSERT INTO shared_lists
                            (room_id, item, added_by, added_at, completed)
                            VALUES ($1, $2, $3, $4, false)
                        """, room_id, item.strip(), sender, ts)

    async def get_list(self, room_id: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT item, added_by, added_at, completed
                FROM shared_lists
                WHERE room_id = $1
                ORDER BY completed ASC, added_at DESC
            """, room_id)
            return [dict(r) for r in rows]

    async def mark_item_done(self, room_id: str, item_name: str) -> Optional[str]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                UPDATE shared_lists
                SET completed = true, completed_at = NOW()
                WHERE room_id = $1
                AND item ILIKE $2
                AND completed = false
                RETURNING item
            """, room_id, f'%{item_name}%')
            return row['item'] if row else None

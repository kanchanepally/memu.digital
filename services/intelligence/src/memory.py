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

        -- 4. Backup History
        CREATE TABLE IF NOT EXISTS backup_history (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            size_bytes BIGINT NOT NULL,
            status TEXT NOT NULL,
            error TEXT,
            duration_seconds INT,
            usb_copied_at TIMESTAMP,
            notification_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_backup_created ON backup_history(created_at DESC);
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

    # =========================================================================
    # Backup History Methods
    # =========================================================================

    async def record_backup(
        self,
        filename: str,
        size_bytes: int,
        status: str,
        duration_seconds: int,
        error: Optional[str] = None
    ):
        """Record a backup attempt in the database.

        Args:
            filename: Name of the backup archive file
            size_bytes: Size of the backup in bytes
            status: 'success', 'failed', or 'in_progress'
            duration_seconds: How long the backup took
            error: Error message if backup failed
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO backup_history
                (filename, size_bytes, status, duration_seconds, error)
                VALUES ($1, $2, $3, $4, $5)
            """, filename, size_bytes, status, duration_seconds, error)
        logger.info(f"Recorded backup: {filename} ({status})")

    async def get_latest_backup(self) -> Optional[Dict[str, Any]]:
        """Get the most recent backup record.

        Returns:
            Dictionary with backup details, or None if no backups exist
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, filename, size_bytes, status, error,
                       duration_seconds, usb_copied_at, notification_sent, created_at
                FROM backup_history
                ORDER BY created_at DESC
                LIMIT 1
            """)
            return dict(row) if row else None

    async def get_backup_count(self) -> int:
        """Get the total number of successful backups stored locally.

        Returns:
            Number of successful backup records
        """
        async with self.pool.acquire() as conn:
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM backup_history
                WHERE status = 'success'
            """)
            return count or 0

    async def get_total_backup_size(self) -> int:
        """Get the total size of all successful backups.

        Returns:
            Total size in bytes, or 0 if no backups
        """
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("""
                SELECT SUM(size_bytes) FROM backup_history
                WHERE status = 'success'
            """)
            return total or 0

    async def mark_usb_copied(self, backup_id: int):
        """Mark a backup as copied to USB drive.

        Args:
            backup_id: ID of the backup record to update
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE backup_history
                SET usb_copied_at = NOW()
                WHERE id = $1
            """, backup_id)
        logger.info(f"Marked backup {backup_id} as copied to USB")

    async def get_unnotified_failures(self) -> List[Dict[str, Any]]:
        """Get failed backups that haven't been notified yet.

        Returns:
            List of failed backup records needing notification
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, filename, error, created_at
                FROM backup_history
                WHERE status = 'failed'
                AND notification_sent = FALSE
                ORDER BY created_at DESC
            """)
            return [dict(r) for r in rows]

    async def mark_notification_sent(self, backup_id: int):
        """Mark a backup's failure notification as sent.

        Args:
            backup_id: ID of the backup record to update
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE backup_history
                SET notification_sent = TRUE
                WHERE id = $1
            """, backup_id)
        logger.info(f"Marked notification sent for backup {backup_id}")

    async def get_last_usb_backup_time(self) -> Optional[datetime]:
        """Get the timestamp of the most recent USB backup.

        Returns:
            Datetime of last USB backup, or None if never backed up to USB
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT MAX(usb_copied_at)
                FROM backup_history
                WHERE usb_copied_at IS NOT NULL
            """)
            return result

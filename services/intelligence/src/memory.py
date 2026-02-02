import logging
import asyncpg
import aiohttp
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

    # =========================================================================
    # REMINDERS
    # =========================================================================

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

    # =========================================================================
    # FACTS (Explicit /remember)
    # =========================================================================

    async def remember_fact(self, room_id: str, sender: str, fact: str):
        async with self.pool.acquire() as conn:
            ts = int(datetime.now().timestamp() * 1000)
            await conn.execute("""
                INSERT INTO household_memory (room_id, fact, created_by, created_at)
                VALUES ($1, $2, $3, $4)
            """, room_id, fact, sender, ts)

    async def recall_facts(self, room_id: str, query: str) -> List[Dict]:
        """Search explicitly saved facts."""
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

    # =========================================================================
    # MATRIX CHAT HISTORY SEARCH (NEW)
    # =========================================================================

    async def search_chat_history(self, room_id: str, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Matrix chat history using Synapse's search API.
        This searches actual conversation messages, not just /remember facts.
        
        Uses the Matrix Client-Server API:
        POST /_matrix/client/v3/search
        """
        if not Config.MATRIX_BOT_TOKEN:
            logger.warning("No bot token configured, cannot search chat history")
            return []

        search_url = f"{Config.MATRIX_HOMESERVER_URL}/_matrix/client/v3/search"
        
        headers = {
            "Authorization": f"Bearer {Config.MATRIX_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Matrix search request body
        search_body = {
            "search_categories": {
                "room_events": {
                    "search_term": query,
                    "filter": {
                        "rooms": [room_id]
                    },
                    "order_by": "recent",
                    "event_context": {
                        "before_limit": 1,
                        "after_limit": 1,
                        "include_profile": True
                    }
                }
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(search_url, json=search_body, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_matrix_search_results(data, limit)
                    elif resp.status == 404:
                        # Search endpoint might not be available, try fallback
                        logger.info("Matrix search API not available, using message fetch fallback")
                        return await self._fallback_message_search(room_id, query, limit)
                    else:
                        error_text = await resp.text()
                        logger.error(f"Matrix search failed ({resp.status}): {error_text}")
                        return []
        except Exception as e:
            logger.error(f"Matrix search error: {e}")
            return []

    def _parse_matrix_search_results(self, data: Dict, limit: int) -> List[Dict]:
        """Parse Matrix search API response into simple result list."""
        results = []
        
        try:
            room_events = data.get("search_categories", {}).get("room_events", {})
            hits = room_events.get("results", [])
            
            for hit in hits[:limit]:
                event = hit.get("result", {})
                content = event.get("content", {})
                
                # Only include text messages
                if content.get("msgtype") == "m.text":
                    results.append({
                        "sender": event.get("sender", "unknown"),
                        "body": content.get("body", ""),
                        "timestamp": event.get("origin_server_ts", 0),
                        "event_id": event.get("event_id", ""),
                        "source": "chat"  # Mark as from chat history
                    })
        except Exception as e:
            logger.error(f"Error parsing Matrix search results: {e}")
        
        return results

    async def _fallback_message_search(self, room_id: str, query: str, limit: int) -> List[Dict]:
        """
        Fallback: Fetch recent messages and search locally.
        Used when Matrix search API is not available.
        """
        messages_url = f"{Config.MATRIX_HOMESERVER_URL}/_matrix/client/v3/rooms/{room_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {Config.MATRIX_BOT_TOKEN}"
        }
        
        params = {
            "dir": "b",  # Backwards from most recent
            "limit": 100  # Fetch last 100 messages to search
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(messages_url, params=params, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._local_search_messages(data.get("chunk", []), query, limit)
                    else:
                        logger.error(f"Message fetch failed ({resp.status})")
                        return []
        except Exception as e:
            logger.error(f"Message fetch error: {e}")
            return []

    def _local_search_messages(self, messages: List[Dict], query: str, limit: int) -> List[Dict]:
        """Search through fetched messages locally (case-insensitive)."""
        results = []
        query_lower = query.lower()
        
        for msg in messages:
            content = msg.get("content", {})
            if content.get("msgtype") != "m.text":
                continue
                
            body = content.get("body", "")
            if query_lower in body.lower():
                results.append({
                    "sender": msg.get("sender", "unknown"),
                    "body": body,
                    "timestamp": msg.get("origin_server_ts", 0),
                    "event_id": msg.get("event_id", ""),
                    "source": "chat"
                })
                
                if len(results) >= limit:
                    break
        
        return results

    async def unified_recall(self, room_id: str, query: str) -> Dict[str, List[Dict]]:
        """
        Unified recall: searches both saved facts AND chat history.
        Returns results grouped by source.
        """
        # Search saved facts (explicit /remember)
        facts = await self.recall_facts(room_id, query)
        
        # Search chat history (actual conversations)
        chat_results = await self.search_chat_history(room_id, query, limit=5)
        
        return {
            "facts": facts,
            "chat": chat_results
        }

    # =========================================================================
    # SHARED LISTS
    # =========================================================================

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

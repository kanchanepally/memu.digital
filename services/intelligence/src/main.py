# services/intelligence/src/main.py
"""
Memu Intelligence Service
Processes messages locally using AI without sending data to external services.
"""

import os
import asyncio
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import httpx
import dateparser

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
if not log_level:
    log_level = "INFO"

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memu.intelligence")


class MemuIntelligence:
    """Main intelligence service that processes messages and executes AI commands."""

    def __init__(self):
        self.db_host = os.getenv("DB_HOST", "database")
        self.db_name = os.getenv("DB_NAME", "immich")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "postgres")
        self.ollama_url = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.ai_enabled = os.getenv("AI_ENABLED", "true").lower() == "true"
        self.ai_timeout = int(os.getenv("AI_TIMEOUT", "30"))
        
        self.hs_url = os.getenv("MATRIX_HOMESERVER_URL", "http://synapse:8008")
        self.bot_token = os.getenv("MATRIX_BOT_TOKEN", "")

    def get_db_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

    async def execute_action(self, action: Dict):
        """Execute the action returned by process_message."""
        if action['action'] == 'send_message':
            await self.send_matrix_message(action['room_id'], action['content'])

    async def check_invites(self):
        """Check for room invitations and join them."""
        if not self.hs_url or not self.bot_token:
            return

        url = f"{self.hs_url}/_matrix/client/r0/sync"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {self.bot_token}"},
                    params={"timeout": 0, "filter": '{"room":{"include_leave":false,"timeline":{"limit":1}}}'}
                )
                if response.status_code == 200:
                    data = response.json()
                    invites = data.get("rooms", {}).get("invite", {})
                    for room_id in invites:
                        logger.info(f"Found invite for room {room_id}. Joining...")
                        await self.join_room(room_id)
        except Exception as e:
            logger.error(f"Error checking invites: {e}")

    async def join_room(self, room_id: str):
        url = f"{self.hs_url}/_matrix/client/r0/rooms/{room_id}/join"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {self.bot_token}"},
                    json={}
                )
                if response.status_code == 200:
                    logger.info(f"Successfully joined room {room_id}")
                else:
                    logger.error(f"Failed to join room {room_id}: {response.text}")
        except Exception as e:
            logger.error(f"Error joining room {room_id}: {e}")

    async def send_matrix_message(self, room_id: str, content: str):
        """Send a message to a Matrix room."""
        if not self.hs_url or not self.bot_token:
            logger.error("Cannot send message: Matrix configuration missing")
            return

        url = f"{self.hs_url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.bot_token}"
                    },
                    json={
                        "msgtype": "m.text",
                        "body": content
                    }
                )
                response.raise_for_status()
                logger.info(f"Sent message to {room_id}")
        except Exception as e:
            logger.error(f"Failed to send Matrix message: {e}")

    async def process_message(self, message: Dict) -> Optional[Dict]:
        """
        Process a single message and determine action.
        
        Args:
            message: Dict with keys: id, room_id, sender, content, timestamp
            
        Returns:
            Action dict if command detected, None otherwise
        """
        content = message.get('content', '').strip()
        
        # Quick command detection (no AI needed for explicit commands)
        if content.startswith('/remember'):
            return await self.handle_remember(message)
        elif content.startswith('/recall'):
            return await self.handle_recall(message)
        elif content.startswith('/addtolist'):
            return await self.handle_add_to_list(message)
        elif content.startswith('/showlist'):
            return await self.handle_show_list(message)
        elif content.startswith('/remind'):
            return await self.handle_remind(message)
        elif content.startswith('/done'):
            return await self.handle_mark_done(message)
        elif content.startswith('/summarize'):
            summary = await self.generate_daily_summary(message['room_id'])
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': summary
            }
        
        # For natural language detection, use AI if enabled
        if self.ai_enabled and await self.contains_implicit_command(content):
            return await self.handle_natural_language(message)
        
        return None
    
    async def handle_remind(self, message: Dict) -> Dict:
        """
        Set a reminder using AI to extract time and task.
        
        Example: "/remind me to call Mom tomorrow at 5pm"
        """
        content = message['content'].replace('/remind', '').strip()
        
        task = content
        dt = None
        
        # 1. Try to use AI to extract task and time
        if self.ai_enabled:
            try:
                async with httpx.AsyncClient(timeout=self.ai_timeout) as client:
                    response = await client.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            'model': self.model,
                            'prompt': f"""Extract the task and the time from this reminder request.

Request: "{content}"

Respond ONLY with valid JSON in this format:
{{
    "task": "what to do",
    "time": "when to do it"
}}

Example:
Request: "remind me to check the oven in 1 minute"
Response: {{"task": "check the oven", "time": "in 1 minute"}}

Your JSON response:""",
                            'stream': False,
                            'options': {'temperature': 0.1}
                        }
                    )
                    
                    result = response.json()
                    ai_text = result.get('response', '{}').strip()
                    # Clean up markdown if present
                    if ai_text.startswith('```json'):
                        ai_text = ai_text[7:]
                    if ai_text.endswith('```'):
                        ai_text = ai_text[:-3]
                        
                    extracted = json.loads(ai_text)
                    
                    if extracted.get('time'):
                        task = extracted.get('task', content)
                        time_str = extracted.get('time')
                        dt = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})
            except Exception as e:
                logger.error(f"AI extraction failed: {e}")

        # 2. Fallback: If AI failed or disabled, try parsing the whole string
        if not dt:
            # Remove "me to" for cleaner parsing
            clean_content = content
            if clean_content.lower().startswith('me to '):
                clean_content = clean_content[6:]
            dt = dateparser.parse(clean_content, settings={'PREFER_DATES_FROM': 'future'})

        if not dt:
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ I could not understand the time. Try: "/remind call Mom tomorrow at 5pm"'
            }
            
        # If date is in past, maybe they meant tomorrow?
        if dt < datetime.now():
            dt = dateparser.parse(content, settings={'PREFER_DATES_FROM': 'future', 'PREFER_DAY_OF_MONTH': 'first'})
            
        if not dt or dt < datetime.now():
             return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ That time is in the past!'
            }

        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO reminders (room_id, user_id, content, due_at)
                VALUES (%s, %s, %s, %s)
            """, (
                message['room_id'],
                message['sender'],
                task,
                dt
            ))
            conn.commit()
            
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': f'⏰ Reminder set for {dt.strftime("%Y-%m-%d %H:%M")}: "{task}"'
            }
        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Failed to set reminder'
            }
        finally:
            cursor.close()
            conn.close()

    async def check_reminders(self):
        """Check for due reminders and send notifications."""
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT id, room_id, user_id, content
                FROM reminders
                WHERE due_at <= NOW() AND processed = FALSE
            """)
            
            reminders = cursor.fetchall()
            
            for rem in reminders:
                logger.info(f"Sending reminder {rem['id']} to {rem['room_id']}")
                
                # Send message
                await self.send_matrix_message(
                    rem['room_id'], 
                    f"🔔 REMINDER: {rem['content']}"
                )
                
                # Mark processed
                cursor.execute("UPDATE reminders SET processed = TRUE WHERE id = %s", (rem['id'],))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
        finally:
            cursor.close()
            conn.close()

    async def handle_remember(self, message: Dict) -> Dict:
        """
        Store a fact in the household memory.
        
        Example: "/remember the wifi password is MySecurePass123"
        """
        content = message['content']
        fact = content.replace('/remember', '').strip()
        
        if not fact:
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Usage: /remember [fact to remember]'
            }
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO household_memory (room_id, fact, created_by, created_at)
                VALUES (%s, %s, %s, %s)
            """, (
                message['room_id'],
                fact,
                message['sender'],
                message['timestamp']
            ))
            conn.commit()
            logger.info(f"Stored memory in {message['room_id']}: {fact[:50]}...")
            
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': f'✓ Remembered: {fact}'
            }
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            conn.rollback()
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Failed to store memory'
            }
        finally:
            cursor.close()
            conn.close()
    
    async def handle_recall(self, message: Dict) -> Dict:
        """
        Retrieve stored facts using keyword search.
        
        Example: "/recall wifi password"
        """
        query = message['content'].replace('/recall', '').strip()
        
        if not query:
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Usage: /recall [what to search for]'
            }
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT fact, created_at, created_by
                FROM household_memory 
                WHERE room_id = %s 
                AND fact ILIKE %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (message['room_id'], f'%{query}%'))
            
            results = cursor.fetchall()
            
            if not results:
                return {
                    'action': 'send_message',
                    'room_id': message['room_id'],
                    'content': f"🤔 I don't remember anything about '{query}'"
                }
            
            # Format results
            response = f"💡 Here's what I remember about '{query}':\n\n"
            for row in results:
                created = row['created_at'].strftime('%Y-%m-%d')
                response += f"• {row['fact']} (saved {created})\n"
            
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': response
            }
        except Exception as e:
            logger.error(f"Error recalling memory: {e}")
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Failed to recall memory'
            }
        finally:
            cursor.close()
            conn.close()
    
    async def handle_add_to_list(self, message: Dict) -> Dict:
        """
        Add items to a shared list.
        
        Example: "/addtolist milk, bread, eggs"
        """
        content = message['content'].replace('/addtolist', '').strip()
        
        if not content:
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Usage: /addtolist [item1, item2, ...]'
            }
        
        items = [item.strip() for item in content.split(',')]
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            for item in items:
                if item:  # Skip empty items
                    cursor.execute("""
                        INSERT INTO shared_lists 
                        (room_id, item, added_by, added_at, completed)
                        VALUES (%s, %s, %s, %s, false)
                    """, (
                        message['room_id'],
                        item,
                        message['sender'],
                        message['timestamp']
                    ))
            conn.commit()
            
            logger.info(f"Added {len(items)} items to list in {message['room_id']}")
            
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': f'✓ Added {len(items)} item(s) to the shopping list'
            }
        except Exception as e:
            logger.error(f"Error adding to list: {e}")
            conn.rollback()
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Failed to add items'
            }
        finally:
            cursor.close()
            conn.close()
    
    async def handle_show_list(self, message: Dict) -> Dict:
        """Show the current shopping list."""
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT item, added_by, added_at, completed
                FROM shared_lists
                WHERE room_id = %s
                ORDER BY completed ASC, added_at DESC
            """, (message['room_id'],))
            
            results = cursor.fetchall()
            
            if not results:
                return {
                    'action': 'send_message',
                    'room_id': message['room_id'],
                    'content': '📝 Shopping list is empty'
                }
            
            # Format list
            active_items = [r for r in results if not r['completed']]
            completed_items = [r for r in results if r['completed']]
            
            response = "📝 Shopping List:\n\n"
            
            if active_items:
                response += "To Buy:\n"
                for item in active_items:
                    response += f"⬜ {item['item']}\n"
            
            if completed_items:
                response += "\nCompleted:\n"
                for item in completed_items[:5]:  # Show last 5 completed
                    response += f"☑ {item['item']}\n"
            
            response += f"\nTotal items: {len(active_items)} active"
            
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': response
            }
        except Exception as e:
            logger.error(f"Error showing list: {e}")
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Failed to retrieve list'
            }
        finally:
            cursor.close()
            conn.close()
    
    async def handle_mark_done(self, message: Dict) -> Dict:
        """Mark list item as done."""
        item_name = message['content'].replace('/done', '').strip()
        
        if not item_name:
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Usage: /done [item name]'
            }
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE shared_lists
                SET completed = true, completed_at = NOW()
                WHERE room_id = %s 
                AND item ILIKE %s 
                AND completed = false
                RETURNING item
            """, (message['room_id'], f'%{item_name}%'))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return {
                    'action': 'send_message',
                    'room_id': message['room_id'],
                    'content': f'✓ Marked as done: {result[0]}'
                }
            else:
                return {
                    'action': 'send_message',
                    'room_id': message['room_id'],
                    'content': f"❌ Item '{item_name}' not found in list"
                }
        except Exception as e:
            logger.error(f"Error marMemug done: {e}")
            conn.rollback()
            return {
                'action': 'send_message',
                'room_id': message['room_id'],
                'content': '❌ Failed to mark item as done'
            }
        finally:
            cursor.close()
            conn.close()
    
    async def contains_implicit_command(self, content: str) -> bool:
        """
        Use local AI to detect if message contains an implicit command.
        
        Example: "We need milk and bread" -> Should detect LIST
        """
        if not self.ai_enabled:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=self.ai_timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        'model': self.model,
                        'prompt': f"""Analyze this message and determine if it contains an implicit command or action item.

Message: "{content}"

Respond with ONLY one word: CALENDAR, LIST, REMINDER, or NONE

Examples:
"Let's have dinner Friday at 7pm" -> CALENDAR
"We need milk and bread" -> LIST
"Remind me to call mom tomorrow" -> REMINDER
"How was your day?" -> NONE

Your response:""",
                        'stream': False,
                        'options': {
                            'temperature': 0.1,
                            'num_predict': 10
                        }
                    }
                )
                
                result = response.json()
                detection = result.get('response', 'NONE').strip().upper()
                
                return detection in ['CALENDAR', 'LIST', 'REMINDER']
        except Exception as e:
            logger.error(f"Error detecting implicit command: {e}")
            return False
    
    async def handle_natural_language(self, message: Dict) -> Optional[Dict]:
        """Extract structured data from natural language using local AI."""
        content = message['content']
        
        try:
            async with httpx.AsyncClient(timeout=self.ai_timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        'model': self.model,
                        'prompt': f"""Extract structured information from this message.

Message: "{content}"

Respond ONLY with valid JSON in this exact format:
{{
    "type": "list",
    "items": ["item1", "item2"]
}}

Your JSON response:""",
                        'stream': False,
                        'options': {
                            'temperature': 0.2
                        }
                    }
                )
                
                result = response.json()
                ai_response = result.get('response', '{}')
                
                # Parse AI response
                extracted = json.loads(ai_response)
                
                if extracted.get('type') == 'list' and extracted.get('items'):
                    # Automatically add to list
                    items = extracted['items']
                    conn = self.get_db_connection()
                    cursor = conn.cursor()
                    
                    for item in items:
                        cursor.execute("""
                            INSERT INTO shared_lists 
                            (room_id, item, added_by, added_at, completed)
                            VALUES (%s, %s, %s, %s, false)
                        """, (
                            message['room_id'],
                            item,
                            message['sender'],
                            message['timestamp']
                        ))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    return {
                        'action': 'send_message',
                        'room_id': message['room_id'],
                        'content': f'✓ Added {len(items)} item(s) to shopping list: {", ".join(items)}'
                    }
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON")
        except Exception as e:
            logger.error(f"Error in natural language processing: {e}")
        
        return None
    
    async def generate_daily_summary(self, room_id: str) -> str:
        """Generate a daily summary of activity for a room."""
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT sender, content, timestamp
                FROM messages
                WHERE room_id = %s
                AND timestamp >= CURRENT_DATE
                ORDER BY timestamp ASC
            """, (room_id,))
            
            messages = cursor.fetchall()
            
            if not messages:
                return "No activity today."
            
            # Build context for AI
            context = f"Today's messages ({len(messages)} total):\n\n"
            for msg in messages[:50]:  # Limit context
                sender_name = msg['sender'].split(':')[0].replace('@', '')
                context += f"{sender_name}: {msg['content']}\n"
            
            if not self.ai_enabled:
                return f"Activity summary: {len(messages)} messages exchanged today."
            
            # Ask AI to summarize
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        'model': self.model,
                        'prompt': f"""Summarize today's family/class activity in 2-3 sentences.
Focus on: important events, decisions made, upcoming plans.

{context}

Summary:""",
                        'stream': False,
                        'options': {
                            'temperature': 0.7,
                            'num_predict': 150
                        }
                    }
                )
                
                result = response.json()
                summary = result.get('response', '').strip()
                
                return summary or f"Activity summary: {len(messages)} messages exchanged today."
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Failed to generate summary."
        finally:
            cursor.close()
            conn.close()


async def main():
    """Main event loop that processes new messages from the database."""
    intelligence = MemuIntelligence()
    
    logger.info("Memu Intelligence Service starting...")
    logger.info("Waiting for database connection...")
    
    # Wait for database to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = intelligence.get_db_connection()
            conn.close()
            logger.info("Database connection established")
            break
        except Exception as e:
            if i == max_retries - 1:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                return
            logger.warning(f"Waiting for database... ({i+1}/{max_retries})")
            await asyncio.sleep(5)
    
    logger.info("Intelligence Service ready. Processing messages...")
    
    while True:
        try:
            # Check for invites first
            await intelligence.check_invites()
            
            # Check for reminders
            await intelligence.check_reminders()

            conn = intelligence.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Poll for unprocessed messages
            cursor.execute("""
                SELECT id, room_id, sender, content, timestamp
                FROM messages
                WHERE processed_by_ai = false
                ORDER BY timestamp ASC
                LIMIT 10
            """)
            
            messages = cursor.fetchall()
            cursor.close()
            conn.close()

            for msg in messages:
                try:
                    logger.info(f"Processing message from {msg['sender']}: {msg['content']}")
                    action = await intelligence.process_message(msg)
                    
                    if action:
                        await intelligence.execute_action(action)
                    
                    # Mark as processed
                    conn = intelligence.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE messages SET processed_by_ai = true WHERE id = %s", (msg['id'],))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                except Exception as e:
                    logger.error(f"Error processing message {msg['id']}: {e}")

            await asyncio.sleep(2)
            
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
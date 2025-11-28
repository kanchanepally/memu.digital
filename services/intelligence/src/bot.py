import logging
import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteMemberEvent
from config import Config
from brain import Brain
from memory import MemoryStore
import dateparser
from datetime import datetime

logger = logging.getLogger("memu.bot")

class MemuBot:
    def __init__(self):
        self.client = AsyncClient(
            Config.MATRIX_HOMESERVER_URL,
            Config.MATRIX_BOT_USERNAME
        )
        self.client.access_token = Config.MATRIX_BOT_TOKEN
        self.brain = Brain()
        self.memory = MemoryStore()

    async def start(self):
        logger.info("Starting MemuBot...")
        await self.memory.connect()
        await self.memory.init_db()  # Ensure tables exist

        # Add callbacks
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_event_callback(self.invite_callback, InviteMemberEvent)

        # Start reminder checker loop in background
        asyncio.create_task(self.check_reminders_loop())

        try:
            # Sync forever
            await self.client.sync_forever(timeout=30000)
        except Exception as e:
            logger.error(f"Sync failed: {e}")
        finally:
            await self.client.close()
            await self.memory.close()

    async def invite_callback(self, room: MatrixRoom, event: InviteMemberEvent):
        """Auto-join rooms when invited."""
        logger.info(f"Invited to room {room.room_id} by {event.sender}. Joining...")
        await self.client.join(room.room_id)

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        # Ignore messages from self
        if event.sender == self.client.user_id:
            return

        logger.info(f"Received message in {room.room_id}: {event.body}")

        # Process command
        await self.process_message(room.room_id, event.sender, event.body)

    async def send_text(self, room_id: str, text: str):
        await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": text
            }
        )

    async def process_message(self, room_id: str, sender: str, content: str):
        content = content.strip()

        if content.startswith('/remember'):
            await self.handle_remember(room_id, sender, content)
        elif content.startswith('/recall'):
            await self.handle_recall(room_id, content)
        elif content.startswith('/addtolist'):
            await self.handle_add_to_list(room_id, sender, content)
        elif content.startswith('/showlist'):
            await self.handle_show_list(room_id)
        elif content.startswith('/remind'):
            await self.handle_remind(room_id, sender, content)
        elif content.startswith('/done'):
            await self.handle_mark_done(room_id, content)
        elif content.startswith('/summarize'):
            await self.handle_summarize(room_id)
        else:
            # Implicit check
            intent = await self.brain.analyze_intent(content)
            if intent == 'LIST':
                 # Try to extract items
                 pass

    async def handle_remember(self, room_id: str, sender: str, content: str):
        fact = content.replace('/remember', '').strip()
        if not fact:
            await self.send_text(room_id, "❌ Usage: /remember [fact]")
            return

        await self.memory.remember_fact(room_id, sender, fact)
        await self.send_text(room_id, f"✓ Remembered: {fact}")

    async def handle_recall(self, room_id: str, content: str):
        query = content.replace('/recall', '').strip()
        if not query:
            await self.send_text(room_id, "❌ Usage: /recall [query]")
            return

        facts = await self.memory.recall_facts(room_id, query)
        if not facts:
            await self.send_text(room_id, f"🤔 I don't remember anything about '{query}'")
            return

        response = f"💡 Here's what I remember about '{query}':\n\n"
        for fact in facts:
            # Handle timestamp (bigint ms or datetime)
            ts = fact['created_at']
            if isinstance(ts, int):
                dt = datetime.fromtimestamp(ts / 1000)
            else:
                dt = ts
            response += f"• {fact['fact']} (saved {dt.strftime('%Y-%m-%d')})\n"

        await self.send_text(room_id, response)

    async def handle_add_to_list(self, room_id: str, sender: str, content: str):
        raw = content.replace('/addtolist', '').strip()
        if not raw:
            await self.send_text(room_id, "❌ Usage: /addtolist item1, item2")
            return

        items = [i.strip() for i in raw.split(',')]
        await self.memory.add_to_list(room_id, sender, items)
        await self.send_text(room_id, f"✓ Added {len(items)} item(s) to the list.")

    async def handle_show_list(self, room_id: str):
        items = await self.memory.get_list(room_id)
        if not items:
            await self.send_text(room_id, "📝 List is empty.")
            return

        active = [i for i in items if not i['completed']]
        completed = [i for i in items if i['completed']]

        response = "📝 Shopping List:\n\n"
        if active:
            response += "To Buy:\n" + "\n".join([f"⬜ {i['item']}" for i in active])
        if completed:
            response += "\n\nCompleted:\n" + "\n".join([f"☑ {i['item']}" for i in completed[:5]])

        await self.send_text(room_id, response)

    async def handle_mark_done(self, room_id: str, content: str):
        item = content.replace('/done', '').strip()
        if not item:
            await self.send_text(room_id, "❌ Usage: /done [item]")
            return

        result = await self.memory.mark_item_done(room_id, item)
        if result:
            await self.send_text(room_id, f"✓ Marked as done: {result}")
        else:
            await self.send_text(room_id, f"❌ Could not find item '{item}'")

    async def handle_remind(self, room_id: str, sender: str, content: str):
        raw = content.replace('/remind', '').strip()

        # Try AI extraction first
        data = await self.brain.extract_reminder(raw)
        task = data.get('task', raw)
        time_str = data.get('time')

        dt = None
        if time_str:
            dt = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})

        # Fallback
        if not dt:
             # Remove "me to"
             clean = raw
             if clean.lower().startswith('me to '):
                 clean = clean[6:]
             dt = dateparser.parse(clean, settings={'PREFER_DATES_FROM': 'future'})

        if not dt or dt < datetime.now():
            await self.send_text(room_id, "❌ I couldn't understand the time or it is in the past.")
            return

        await self.memory.add_reminder(room_id, sender, task, dt)
        await self.send_text(room_id, f"⏰ Reminder set for {dt.strftime('%Y-%m-%d %H:%M')}: \"{task}\"")

    async def handle_summarize(self, room_id: str):
        # Fix: Need to use sync token or context.
        # Using client.room_messages with a start token.
        # Since we don't persist tokens, we can try to use client.room_context which is easier,
        # or use the last synced batch.
        # However, client.next_batch is updated on sync.

        if not self.client.next_batch:
            # If we haven't synced yet, we can't fetch back.
            await self.send_text(room_id, "⚠️ I need to sync first before summarizing history.")
            return

        resp = await self.client.room_messages(
            room_id,
            start=self.client.next_batch,
            direction='b', # Backwards from now
            limit=50
        )

        if isinstance(resp, str): # Error in some matrix-nio versions, or RoomMessagesError
             logger.error(f"Failed to fetch history: {resp}")
             await self.send_text(room_id, "❌ Failed to fetch history.")
             return

        if hasattr(resp, 'chunk'):
            msgs = []
            # Chunk is reversed in time usually (newest first for 'b'?) No, matrix-nio returns them in order usually?
            # Actually, standard CS API returns them in reverse chronological order if dir='b'.
            # Let's reverse them to be chronological.
            for event in reversed(resp.chunk):
                if isinstance(event, RoomMessageText):
                    msgs.append(f"{event.sender}: {event.body}")

            if not msgs:
                await self.send_text(room_id, "No recent activity to summarize.")
                return

            context = "\n".join(msgs)
            summary = await self.brain.summarize_chat(context)
            await self.send_text(room_id, f"📋 Summary:\n{summary}")
        else:
            await self.send_text(room_id, "❌ Failed to fetch history (API error).")

    async def check_reminders_loop(self):
        while True:
            try:
                reminders = await self.memory.get_due_reminders()
                for rem in reminders:
                    await self.send_text(rem['room_id'], f"🔔 REMINDER: {rem['content']}")
                    await self.memory.mark_reminder_processed(rem['id'])
            except Exception as e:
                logger.error(f"Error checking reminders: {e}")

            await asyncio.sleep(10)

import logging
import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteMemberEvent
from config import Config
from brain import Brain
from memory import MemoryStore
from backup_manager import BackupManager
import dateparser
from datetime import datetime, timedelta

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
        self.backup_manager = BackupManager(self.memory)
        self._last_usb_reminder_sent = None  # Track when we last sent USB reminder

    async def start(self):
        logger.info("Starting MemuBot...")
        await self.memory.connect()
        await self.memory.init_db()  # Ensure tables exist

        # Add callbacks
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_event_callback(self.invite_callback, InviteMemberEvent)

        # Start reminder checker loop in background
        asyncio.create_task(self.check_reminders_loop())

        # Start backup notification checker loop
        asyncio.create_task(self.check_backup_notifications_loop())

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
        elif content.startswith('/backup-status') or content.startswith('/backupstatus'):
            await self.handle_backup_status(room_id)
        elif content.startswith('/help'):
            await self.handle_help(room_id)
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

    async def handle_backup_status(self, room_id: str):
        """Show backup status to the user."""
        try:
            status = await self.backup_manager.get_status()
            message = self.backup_manager.format_status_message(status)
            await self.send_text(room_id, message)
        except Exception as e:
            logger.error(f"Error getting backup status: {e}")
            await self.send_text(room_id, "Failed to get backup status. Please check system logs.")

    async def handle_help(self, room_id: str):
        """Show available commands."""
        help_text = """**Memu Bot Commands**

**Memory**
/remember [fact] - Save a fact
/recall [query] - Search saved facts

**Lists**
/addtolist item1, item2 - Add items to shopping list
/showlist - Show the shopping list
/done [item] - Mark item as complete

**Reminders**
/remind [task] [time] - Set a reminder

**Utilities**
/summarize - Summarize recent chat
/backup-status - Check backup health
/help - Show this help"""

        await self.send_text(room_id, help_text)

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

    async def check_backup_notifications_loop(self):
        """Check for backup failures, USB events, and send notifications."""
        # Wait for initial sync to complete
        await asyncio.sleep(30)

        while True:
            try:
                # Check for unnotified backup failures
                failures = await self.backup_manager.get_unnotified_failures()

                for failure in failures:
                    message = self.backup_manager.format_failure_message(failure)
                    await self._broadcast_to_rooms(message)
                    await self.backup_manager.mark_notification_sent(failure['id'])
                    logger.info(f"Sent backup failure notification for {failure['filename']}")

                # Check for USB drive detection
                if await self.backup_manager.check_usb_detected():
                    logger.info("USB drive detected, initiating backup copy...")
                    result = await self.backup_manager.handle_usb_backup()

                    if result:
                        if result.get('status') == 'success':
                            message = self.backup_manager.format_usb_success_message(result)
                        else:
                            message = self.backup_manager.format_usb_error_message(result)
                        await self._broadcast_to_rooms(message)

                # Check for weekly USB reminder (Sunday between 9-11am)
                await self._check_weekly_usb_reminder()

            except Exception as e:
                logger.error(f"Error checking backup notifications: {e}")

            # Check every 30 seconds for USB, 5 minutes overall is too slow for USB detection
            await asyncio.sleep(30)

    async def _check_weekly_usb_reminder(self):
        """Send weekly USB backup reminder on Sunday mornings if overdue."""
        now = datetime.now()

        # Only send on Sunday (weekday 6) between 9am and 11am
        if now.weekday() != 6 or now.hour < 9 or now.hour >= 11:
            return

        # Don't send more than once per day
        if self._last_usb_reminder_sent:
            if (now - self._last_usb_reminder_sent).days < 1:
                return

        # Check if USB reminder should be sent
        if await self.backup_manager.should_send_usb_reminder():
            status = await self.backup_manager.get_status()
            message = self.backup_manager.format_usb_reminder_message(status)
            await self._broadcast_to_rooms(message)
            self._last_usb_reminder_sent = now
            logger.info("Sent weekly USB backup reminder")

    async def _broadcast_to_rooms(self, message: str):
        """Send a message to all joined rooms.

        Args:
            message: Message text to send
        """
        if hasattr(self.client, 'rooms') and self.client.rooms:
            for room_id in self.client.rooms:
                try:
                    await self.send_text(room_id, message)
                except Exception as e:
                    logger.error(f"Failed to send message to {room_id}: {e}")

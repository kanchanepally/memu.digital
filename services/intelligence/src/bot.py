import logging
import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteMemberEvent
from config import Config
from brain import Brain
from memory import MemoryStore
from tools.calendar_tool import CalendarManager
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
        self.calendar = CalendarManager()

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

        content = event.body.strip()
        is_dm = room.member_count == 2
        is_slash = content.startswith('/')

        # In group rooms, only respond to slash commands or @mentions
        bot_display = 'memu'
        bot_mentioned = bot_display.lower() in content.lower() or (
            self.client.user_id and self.client.user_id.split(':')[0].lstrip('@').lower() in content.lower()
        )

        if not is_slash and not is_dm and not bot_mentioned:
            return  # Stay silent in group rooms unless addressed

        await self.process_message(room.room_id, event.sender, content)

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
        elif content.startswith('/schedule'):
            await self.handle_schedule(room_id, sender, content)
        elif content.startswith('/calendar'):
            await self.handle_calendar(room_id, content)
        elif content.startswith('/briefing'):
            await self.handle_briefing(room_id, content)
        elif content.startswith('/help'):
            await self.handle_help(room_id)
        else:
            # Natural language — classify intent and dispatch
            result = await self.brain.analyze_intent(content)
            intent = result.get('intent', 'NONE')
            extracted = result.get('content', content)

            if intent == 'CALENDAR':
                await self.handle_calendar(room_id, f'/calendar {extracted}')
            elif intent == 'SCHEDULE':
                await self.handle_schedule(room_id, sender, f'/schedule {extracted}')
            elif intent == 'LIST_ADD':
                await self.handle_add_to_list(room_id, sender, f'/addtolist {extracted}')
            elif intent == 'LIST_SHOW':
                await self.handle_show_list(room_id)
            elif intent == 'REMINDER':
                await self.handle_remind(room_id, sender, f'/remind {extracted}')
            elif intent == 'RECALL':
                await self.handle_recall(room_id, f'/recall {extracted}')
            elif intent == 'REMEMBER':
                await self.handle_remember(room_id, sender, f'/remember {extracted}')
            elif intent == 'SUMMARIZE':
                await self.handle_summarize(room_id)
            elif intent == 'BRIEFING':
                await self.handle_briefing(room_id, '')
            elif intent == 'CHAT':
                response = await self.brain.generate(
                    f'The user said: "{content}". Respond helpfully and briefly as a family assistant.',
                    system_prompt='You are Memu, a friendly family assistant. Keep responses short and warm.'
                )
                if response:
                    await self.send_text(room_id, response)
            # NONE = not addressed to bot or irrelevant, stay silent

    async def handle_remember(self, room_id: str, sender: str, content: str):
        fact = content.replace('/remember', '').strip()
        if not fact:
            await self.send_text(room_id, "❌ Usage: /remember [fact]")
            return

        await self.memory.remember_fact(room_id, sender, fact)
        await self.send_text(room_id, f"✓ Remembered: {fact}")

    async def handle_recall(self, room_id: str, content: str):
        """
        Enhanced recall: searches both saved facts AND chat history.
        """
        query = content.replace('/recall', '').strip()
        if not query:
            await self.send_text(room_id, "❌ Usage: /recall [query]")
            return

        # Use unified recall to search facts + chat history
        results = await self.memory.unified_recall(room_id, query)
        facts = results.get("facts", [])
        chat_results = results.get("chat", [])

        # No results anywhere
        if not facts and not chat_results:
            await self.send_text(room_id, f"🤔 I couldn't find anything about '{query}'")
            return

        # Build response
        response_parts = []

        # Saved facts (explicit /remember)
        if facts:
            response_parts.append(f"💾 **Saved Facts** about '{query}':\n")
            for fact in facts:
                ts = fact['created_at']
                if isinstance(ts, int):
                    dt = datetime.fromtimestamp(ts / 1000)
                else:
                    dt = ts
                response_parts.append(f"• {fact['fact']} (saved {dt.strftime('%Y-%m-%d')})\n")

        # Chat history matches
        if chat_results:
            if facts:
                response_parts.append("\n")  # Separator
            response_parts.append(f"💬 **From chat history** about '{query}':\n")
            for msg in chat_results:
                ts = msg['timestamp']
                if isinstance(ts, int) and ts > 0:
                    dt = datetime.fromtimestamp(ts / 1000)
                    date_str = dt.strftime('%b %d')
                else:
                    date_str = "recently"
                
                # Truncate long messages
                body = msg['body']
                if len(body) > 100:
                    body = body[:100] + "..."
                
                # Extract username from @user:domain format
                sender = msg['sender'].split(':')[0].replace('@', '')
                response_parts.append(f"• {sender}: \"{body}\" ({date_str})\n")

        response = "".join(response_parts)
        
        # If response is very long, ask AI to summarise
        if len(response) > 1500:
            summary = await self.brain.summarize_recall_results(query, response)
            response = f"📋 Here's what I found about '{query}':\n\n{summary}"

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
        if not self.client.next_batch:
            await self.send_text(room_id, "⚠️ I need to sync first before summarizing history.")
            return

        resp = await self.client.room_messages(
            room_id,
            start=self.client.next_batch,
            direction='b',
            limit=50
        )

        if isinstance(resp, str):
            logger.error(f"Failed to fetch history: {resp}")
            await self.send_text(room_id, "❌ Failed to fetch history.")
            return

        if hasattr(resp, 'chunk'):
            msgs = []
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

    async def handle_schedule(self, room_id: str, sender: str, content: str):
        """
        Add an event to the family calendar.
        Example: /schedule Soccer practice Tuesday at 5pm
        """
        raw = content.replace('/schedule', '').strip()
        if not raw:
            await self.send_text(room_id, "❌ Usage: /schedule [event] [time]\nExample: /schedule Soccer practice Tuesday 5pm")
            return

        # Check if calendar is available
        if not await self.calendar.is_available():
            await self.send_text(room_id, "❌ Calendar service is not available. Please try again later.")
            return

        # Use AI to extract event details
        data = await self.brain.extract_calendar_event(raw)

        summary = data.get('summary', raw.split(' at ')[0] if ' at ' in raw else raw[:50])
        date_str = data.get('date', '')
        time_str = data.get('time', '')
        location = data.get('location', '')
        duration_str = data.get('duration')

        # Parse the date and time
        datetime_str = f"{date_str} {time_str}".strip() if date_str or time_str else raw

        dt_start = dateparser.parse(
            datetime_str,
            settings={
                'PREFER_DATES_FROM': 'future',
                'PREFER_DAY_OF_MONTH': 'first',
                'RETURN_AS_TIMEZONE_AWARE': True,
                'TIMEZONE': Config.TIMEZONE
            }
        )

        if not dt_start:
            # Fallback: try to parse just from raw input
            dt_start = dateparser.parse(raw, settings={'PREFER_DATES_FROM': 'future'})

        if not dt_start:
            await self.send_text(room_id, "❌ I couldn't understand the date/time. Try: /schedule Soccer Tuesday 5pm")
            return

        if dt_start < datetime.now(dt_start.tzinfo):
            await self.send_text(room_id, "❌ That time is in the past. Please specify a future time.")
            return

        # Parse duration
        dt_end = None
        if duration_str:
            duration_parsed = dateparser.parse(f"in {duration_str}")
            if duration_parsed:
                duration = duration_parsed - datetime.now()
                dt_end = dt_start + duration

        if dt_end is None:
            dt_end = dt_start + timedelta(hours=1)  # Default 1 hour

        # Create the event
        uid = await self.calendar.add_event(
            summary=summary,
            dt_start=dt_start,
            dt_end=dt_end,
            location=location or ""
        )

        if uid:
            time_display = dt_start.strftime('%A, %B %d at %H:%M')
            location_display = f" at {location}" if location else ""
            await self.send_text(
                room_id,
                f"📅 Added to calendar: **{summary}**{location_display}\n"
                f"⏰ {time_display}"
            )
        else:
            await self.send_text(room_id, "❌ Failed to add event to calendar. Please try again.")

    async def handle_calendar(self, room_id: str, content: str):
        """
        Show calendar events.
        /calendar - Today's events
        /calendar week - This week's events
        /calendar tomorrow - Tomorrow's events
        """
        arg = content.replace('/calendar', '').strip().lower()

        # Check if calendar is available
        if not await self.calendar.is_available():
            await self.send_text(room_id, "❌ Calendar service is not available. Please try again later.")
            return

        if arg == 'week':
            events = await self.calendar.get_upcoming_events(days=7)
            header = "📅 **This Week's Schedule**"
        elif arg == 'tomorrow':
            tomorrow = datetime.now() + timedelta(days=1)
            start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            events = await self.calendar.get_events(start, end)
            header = "📅 **Tomorrow's Schedule**"
        else:
            events = await self.calendar.get_today_events()
            header = "📅 **Today's Schedule**"

        if not events:
            await self.send_text(room_id, f"{header}\n\nNo events scheduled! Time to relax? 😊")
            return

        formatted = self.calendar.format_events_list(events)
        await self.send_text(room_id, f"{header}\n{formatted}")

    async def handle_briefing(self, room_id: str, content: str = ""):
        """
        Generate and send a briefing on-demand.
        /briefing - Generate full AI briefing
        /briefing debug - Show raw data gathered for debugging
        """
        import json
        from agents.briefing import MorningBriefingAgent

        arg = content.replace('/briefing', '').strip().lower()

        try:
            agent = MorningBriefingAgent(self)

            if arg == 'debug':
                # Debug mode: show raw gathered data
                await self.send_text(room_id, "🔍 Gathering briefing data (debug mode)...")
                data = await agent.gather_all()

                debug_output = "**📊 Briefing Debug Data**\n\n"

                # Calendar
                cal = data.get('calendar', {})
                debug_output += f"**📅 Calendar:** {'✅' if cal.get('available') else '❌'} {cal.get('count', 0)} events\n"
                for evt in cal.get('events', [])[:5]:
                    start = evt.get('start')
                    time_str = start.strftime('%H:%M') if hasattr(start, 'strftime') else str(start)
                    debug_output += f"  • {evt.get('summary', 'No title')} at {time_str}\n"

                # Weather
                weather = data.get('weather', {})
                if weather.get('available'):
                    debug_output += f"\n**🌤️ Weather:** {weather.get('icon', '')} {weather.get('temp', '?')}°C, {weather.get('description', 'N/A')}\n"
                else:
                    debug_output += f"\n**🌤️ Weather:** ❌ Not available (API key: {'set' if Config.WEATHER_API_KEY else 'not set'})\n"

                # Shopping List
                shopping = data.get('shopping', {})
                debug_output += f"\n**🛒 Shopping List:** {'✅' if shopping.get('available') else '❌'} {shopping.get('active_count', 0)} items\n"

                # Memories
                memories = data.get('memories', {})
                if memories.get('available'):
                    debug_output += f"\n**📸 Photo Memories:** {memories.get('total_count', 0)} from this day\n"
                else:
                    debug_output += f"\n**📸 Photo Memories:** ❌ Not available (API key: {'set' if Config.IMMICH_API_KEY else 'not set'})\n"

                await self.send_text(room_id, debug_output)
            else:
                # Normal mode: generate full briefing
                await self.send_text(room_id, "🌅 Generating briefing...")
                await agent.deliver(room_id)

        except Exception as e:
            logger.error(f"Failed to generate briefing: {e}")
            await self.send_text(room_id, "❌ Failed to generate briefing. Check the logs for details.")

    async def handle_help(self, room_id: str):
        """Show available commands."""
        help_text = """🤖 **Memu Bot Commands**

**Calendar**
• `/schedule [event] [time]` - Add to family calendar
  Example: `/schedule Soccer practice Tuesday 5pm`
• `/calendar` - Show today's events
• `/calendar week` - Show this week's events
• `/calendar tomorrow` - Show tomorrow's events

**Memory**
• `/remember [fact]` - Save something to remember
• `/recall [query]` - Search saved facts AND chat history

**Lists**
• `/addtolist item1, item2` - Add items to shared list
• `/showlist` - Show current list
• `/done [item]` - Mark item complete

**Reminders**
• `/remind [task] [time]` - Set a reminder
  Example: `/remind call mom tomorrow 3pm`

**Briefings**
• `/briefing` - Get an on-demand family briefing
• `/briefing debug` - Show raw data sources (for troubleshooting)

**Other**
• `/summarize` - AI summary of recent chat
• `/help` - Show this message

💡 You can also just talk to me naturally! Try:
• "What's happening tomorrow?"
• "Add milk and eggs to the list"
• "Remind me to call the dentist Friday"
• "What's the WiFi password?"

In group chats, mention me by name so I know you're talking to me.
"""
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

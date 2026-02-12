import logging
import asyncio
import httpx
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

        # Extract localpart for robust self-detection (e.g. "memu_bot" from "@memu_bot:domain")
        configured = Config.MATRIX_BOT_USERNAME or ""
        self._bot_localpart = configured.split(':')[0].lstrip('@').lower()
        logger.info(f"Bot configured user_id: {configured}")
        logger.info(f"Bot localpart for self-detection: {self._bot_localpart}")

        # AI mode cache: {room_id: mode} — avoids DB hit on every message
        self._ai_mode_cache = {}

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
            # Do an initial sync to resolve the server-side user_id
            await self.client.sync(timeout=10000)
            logger.info(f"Bot resolved user_id after sync: {self.client.user_id}")
            if self.client.user_id and self.client.user_id != Config.MATRIX_BOT_USERNAME:
                logger.warning(
                    f"MATRIX_BOT_USERNAME mismatch: configured={Config.MATRIX_BOT_USERNAME}, "
                    f"server={self.client.user_id} — update .env to use: {self.client.user_id}"
                )
                # Update localpart from server-resolved ID for belt-and-braces safety
                self._bot_localpart = self.client.user_id.split(':')[0].lstrip('@').lower()

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
        # Ignore messages from self — robust multi-layer check
        # Layer 1: exact user_id match (works when .env has correct full ID)
        if event.sender == self.client.user_id:
            return
        # Layer 2: localpart match (catches domain mismatches like
        # @memu_bot:memu.local vs @memu_bot:test15.memu.digital)
        sender_localpart = event.sender.split(':')[0].lstrip('@').lower()
        if self._bot_localpart and sender_localpart == self._bot_localpart:
            logger.warning(
                f"Self-message caught by localpart fallback: "
                f"sender={event.sender}, client.user_id={self.client.user_id} — "
                f"fix MATRIX_BOT_USERNAME in .env to match server domain"
            )
            return

        logger.info(f"Received message in {room.room_id}: {event.body}")

        content = event.body.strip()
        is_dm = room.member_count == 2
        is_slash = content.startswith('/')

        # Prevent processing old messages on startup (older than 60 seconds)
        # Matrix timestamps are in milliseconds
        event_age = datetime.now().timestamp() * 1000 - event.server_timestamp
        if event_age > 60000:
            logger.info(f"Skipping old message (age: {event_age}ms): {content}")
            return

        # Check if bot is mentioned by name
        bot_display = 'memu'
        bot_mentioned = bot_display.lower() in content.lower() or (
            self.client.user_id and self.client.user_id.split(':')[0].lstrip('@').lower() in content.lower()
        )

        # --- AI Volume Control ---
        # Slash commands ALWAYS work in all modes
        if is_slash:
            await self.process_message(room.room_id, event.sender, content)
            return

        # For natural language, check the room's AI mode
        mode = await self._get_ai_mode(room.room_id)

        if mode == 'off':
            return  # Only slash commands in this room

        if mode == 'quiet':
            # Only explicit @mentions get NL processing
            if not bot_mentioned:
                return
        else:
            # 'active' mode (default) — DMs + @mentions in groups
            if not is_dm and not bot_mentioned:
                return

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

    async def _get_ai_mode(self, room_id: str) -> str:
        """Get AI mode for a room, with in-memory cache."""
        if room_id not in self._ai_mode_cache:
            self._ai_mode_cache[room_id] = await self.memory.get_room_ai_mode(room_id)
        return self._ai_mode_cache[room_id]

    async def process_message(self, room_id: str, sender: str, content: str):
        content = content.strip()

        if content.startswith('/ai'):
            await self.handle_ai_mode(room_id, content)
        elif content.startswith('/private'):
            await self.handle_private(room_id)
        elif content.startswith('/remember'):
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
                    system_prompt='You are Memu, a helpful and intelligent family assistant. Be concise, capable, and mature.'
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
        Cross-silo recall: searches saved facts, chat history, calendar events,
        and photo metadata. Synthesises results when multiple sources match.
        """
        query = content.replace('/recall', '').strip()
        if not query:
            await self.send_text(room_id, "❌ Usage: /recall [query]\nExample: /recall sailing")
            return

        # Search all silos in parallel
        results = await self._cross_silo_search(room_id, query)
        facts = results["facts"]
        chat_results = results["chat"]
        calendar_results = results["calendar"]
        photo_results = results["photos"]

        has_facts_chat = bool(facts or chat_results)
        has_calendar = bool(calendar_results)
        has_photos = bool(photo_results)

        silo_count = sum([has_facts_chat, has_calendar, has_photos])

        if silo_count == 0:
            await self.send_text(room_id, f"🤔 I couldn't find anything about '{query}'")
            return

        # Multiple silos - use LLM synthesis for cross-silo intelligence
        if silo_count >= 2:
            context = self._format_cross_silo_context(query, results)
            synthesis = await self.brain.synthesise_cross_silo(query, context)
            if synthesis:
                source_icons = []
                if has_facts_chat:
                    source_icons.append("💾💬")
                if has_calendar:
                    source_icons.append("📅")
                if has_photos:
                    source_icons.append("📸")
                sources = " ".join(source_icons)
                await self.send_text(
                    room_id,
                    f"🔍 **Cross-silo search** for '{query}' ({sources}):\n\n{synthesis}"
                )
                return
            # Fall through to formatted display if synthesis fails

        # Single silo or synthesis failed - format directly
        response_parts = []

        if facts:
            response_parts.append(f"💾 **Saved Facts** about '{query}':\n")
            for fact in facts:
                ts = fact['created_at']
                if isinstance(ts, int):
                    dt = datetime.fromtimestamp(ts / 1000)
                else:
                    dt = ts
                response_parts.append(f"• {fact['fact']} (saved {dt.strftime('%Y-%m-%d')})\n")

        if chat_results:
            if facts:
                response_parts.append("\n")
            response_parts.append(f"💬 **From chat history** about '{query}':\n")
            for msg in chat_results:
                ts = msg['timestamp']
                if isinstance(ts, int) and ts > 0:
                    dt = datetime.fromtimestamp(ts / 1000)
                    date_str = dt.strftime('%b %d')
                else:
                    date_str = "recently"
                body = msg['body']
                if len(body) > 100:
                    body = body[:100] + "..."
                sender = msg['sender'].split(':')[0].replace('@', '')
                response_parts.append(f"• {sender}: \"{body}\" ({date_str})\n")

        if calendar_results:
            if response_parts:
                response_parts.append("\n")
            response_parts.append(f"📅 **Calendar events** matching '{query}':\n")
            for event in calendar_results[:5]:
                date_str = event['start'].strftime('%b %d') if event.get('start') else ''
                time_str = ""
                if event.get('start') and not event.get('all_day'):
                    time_str = event['start'].strftime('%H:%M')
                else:
                    time_str = "All day"
                location = f" @ {event['location']}" if event.get('location') else ""
                response_parts.append(f"• {event['summary']} ({date_str} {time_str}){location}\n")

        if photo_results:
            if response_parts:
                response_parts.append("\n")
            response_parts.append(f"📸 **Photos** matching '{query}':\n")
            count = len(photo_results)
            if count == 1:
                p = photo_results[0]
                date_str = p['date'][:10] if p.get('date') else ''
                city = f" in {p['city']}" if p.get('city') else ''
                response_parts.append(f"• 1 photo{city} ({date_str})\n")
            else:
                cities = set(p['city'] for p in photo_results if p.get('city'))
                dates = [p['date'][:10] for p in photo_results if p.get('date')]
                date_range = f" from {min(dates)} to {max(dates)}" if dates else ""
                location_str = f" in {', '.join(cities)}" if cities else ""
                response_parts.append(f"• {count} photos{location_str}{date_range}\n")

        response = "".join(response_parts)

        # If response is very long, ask AI to summarise
        if len(response) > 1500:
            summary = await self.brain.summarize_recall_results(query, response)
            response = f"📋 Here's what I found about '{query}':\n\n{summary}"

        await self.send_text(room_id, response)

    async def _cross_silo_search(self, room_id, query):
        """Search across all data silos in parallel."""
        results = await asyncio.gather(
            self.memory.unified_recall(room_id, query),
            self._search_calendar(query),
            self._search_photos(query),
            return_exceptions=True
        )

        unified = results[0] if not isinstance(results[0], Exception) else {"facts": [], "chat": []}
        calendar = results[1] if not isinstance(results[1], Exception) else []
        photos = results[2] if not isinstance(results[2], Exception) else []

        if isinstance(results[0], Exception):
            logger.warning(f"Facts/chat search failed: {results[0]}")
        if isinstance(results[1], Exception):
            logger.warning(f"Calendar search failed: {results[1]}")
        if isinstance(results[2], Exception):
            logger.warning(f"Photo search failed: {results[2]}")

        return {
            "facts": unified.get("facts", []),
            "chat": unified.get("chat", []),
            "calendar": calendar,
            "photos": photos,
        }

    async def _search_calendar(self, query):
        """Search calendar events for cross-silo recall."""
        try:
            if not await self.calendar.is_available():
                return []
            return await self.calendar.search_events(query)
        except Exception as e:
            logger.warning(f"Calendar search failed: {e}")
            return []

    async def _search_photos(self, query):
        """Search Immich photos for cross-silo recall."""
        if not Config.IMMICH_API_KEY:
            return []

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"{Config.IMMICH_API_URL}/api/search/smart"
                headers = {'x-api-key': Config.IMMICH_API_KEY}
                response = await client.post(url, headers=headers, json={"query": query})

                if response.status_code == 200:
                    data = response.json()
                    # Handle different Immich response formats
                    if "assets" in data:
                        assets = data["assets"].get("items", [])
                    elif isinstance(data, list):
                        assets = data
                    else:
                        assets = []

                    results = []
                    for asset in assets[:10]:
                        exif = asset.get("exifInfo", {}) or {}
                        results.append({
                            "filename": asset.get("originalFileName", ""),
                            "date": asset.get("localDateTime", ""),
                            "city": exif.get("city", "") or "",
                            "description": exif.get("description", "") or "",
                            "type": asset.get("type", "IMAGE"),
                        })
                    return results
                else:
                    logger.info(f"Immich smart search returned {response.status_code}")
                    return []
        except Exception as e:
            logger.warning(f"Photo search failed: {e}")
            return []

    def _format_cross_silo_context(self, query, results):
        """Format cross-silo results into context for LLM synthesis."""
        parts = []

        facts = results.get("facts", [])
        if facts:
            parts.append("## Saved Facts")
            for fact in facts:
                ts = fact['created_at']
                if isinstance(ts, int):
                    dt = datetime.fromtimestamp(ts / 1000)
                    date_str = dt.strftime('%Y-%m-%d')
                else:
                    date_str = str(ts)
                parts.append(f"- {fact['fact']} (saved {date_str})")

        chat = results.get("chat", [])
        if chat:
            parts.append("\n## Chat History")
            for msg in chat:
                ts = msg['timestamp']
                if isinstance(ts, int) and ts > 0:
                    dt = datetime.fromtimestamp(ts / 1000)
                    date_str = dt.strftime('%b %d')
                else:
                    date_str = "recently"
                sender = msg['sender'].split(':')[0].replace('@', '')
                body = msg['body'][:200]
                parts.append(f"- {sender}: \"{body}\" ({date_str})")

        calendar = results.get("calendar", [])
        if calendar:
            parts.append("\n## Calendar Events")
            for event in calendar[:8]:
                date_str = event['start'].strftime('%b %d, %Y') if event.get('start') else ''
                time_str = ""
                if event.get('start') and not event.get('all_day'):
                    time_str = event['start'].strftime('%H:%M')
                else:
                    time_str = "All day"
                location = f" at {event['location']}" if event.get('location') else ""
                desc = f" - {event['description'][:100]}" if event.get('description') else ""
                parts.append(f"- {event['summary']} ({date_str} {time_str}){location}{desc}")

        photos = results.get("photos", [])
        if photos:
            parts.append("\n## Photos")
            count = len(photos)
            cities = set(p['city'] for p in photos if p.get('city'))
            dates = [p['date'][:10] for p in photos if p.get('date')]

            parts.append(f"- {count} matching photos found")
            if dates:
                parts.append(f"- Date range: {min(dates)} to {max(dates)}")
            if cities:
                parts.append(f"- Locations: {', '.join(cities)}")
            for p in photos[:3]:
                date_str = p['date'][:10] if p.get('date') else 'unknown date'
                city = f" in {p['city']}" if p.get('city') else ""
                desc = f" - {p['description']}" if p.get('description') else ""
                parts.append(f"  - {p['filename']} ({date_str}){city}{desc}")

        return "\n".join(parts)

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

    async def handle_ai_mode(self, room_id: str, content: str):
        """Set how proactive the bot is in this room."""
        VALID_MODES = {'off', 'quiet', 'active'}
        MODE_DESCRIPTIONS = {
            'off': '🔇 **AI Off** — I\'ll only respond to /slash commands in this room.',
            'quiet': '🔉 **AI Quiet** — I\'ll respond to /slash commands and @mentions only.',
            'active': '🔊 **AI Active** — I\'ll respond naturally to messages, mentions, and DMs.',
        }

        arg = content.replace('/ai', '').strip().lower()

        if arg not in VALID_MODES:
            current = await self._get_ai_mode(room_id)
            await self.send_text(
                room_id,
                f"🎚️ **AI Volume Control**\n\n"
                f"Current mode: {MODE_DESCRIPTIONS[current]}\n\n"
                f"**Set a mode:**\n"
                f"• `/ai off` — Slash commands only (silent)\n"
                f"• `/ai quiet` — Slash commands + @mentions\n"
                f"• `/ai active` — Full natural language (default)\n"
            )
            return

        await self.memory.set_room_ai_mode(room_id, arg)
        self._ai_mode_cache[room_id] = arg  # Update cache
        await self.send_text(room_id, MODE_DESCRIPTIONS[arg])

    async def handle_private(self, room_id: str):
        """Explain what Memu already protects."""
        await self.send_text(room_id, """🔒 **Your Privacy on Memu**

**Chat — End-to-end encrypted**
Your messages are encrypted on your device before they're sent. Not even the server admin can read them. This is the same level of encryption as Signal.

**Photos — Separate per person**
Each family member has their own Immich account and photo library. Your photos are only visible to you unless you choose to share them.

**AI — Runs locally**
The AI assistant runs entirely on your family's hardware. Your conversations with it never leave your home. No data is sent to OpenAI, Google, or anyone else.

**Everything — On your hardware**
All data stays on hardware your family owns. There are no cloud services, no subscriptions, and no company that can access, sell, or lose your data.

**Control**
• Use `/ai off` to silence the bot in any room
• Use `/ai quiet` for slash commands and @mentions only
• Every family member can take their data with them (coming soon)
""")

    async def handle_help(self, room_id: str):
        """Show available commands."""
        current_mode = await self._get_ai_mode(room_id)
        mode_display = {'off': '🔇 Off', 'quiet': '🔉 Quiet', 'active': '🔊 Active'}
        help_text = f"""🤖 **Memu Bot Commands**

**Calendar**
• `/schedule [event] [time]` — Add to family calendar
  Example: `/schedule Soccer practice Tuesday 5pm`
• `/calendar` — Show today's events
• `/calendar week` — Show this week's events
• `/calendar tomorrow` — Show tomorrow's events

**Memory & Search**
• `/remember [fact]` — Save something to remember
• `/recall [query]` — Cross-silo search: facts, chat, calendar AND photos

**Lists**
• `/addtolist item1, item2` — Add items to shared list
• `/showlist` — Show current list
• `/done [item]` — Mark item complete

**Reminders**
• `/remind [task] [time]` — Set a reminder
  Example: `/remind call mom tomorrow 3pm`

**Briefings**
• `/briefing` — Get an on-demand family briefing
• `/briefing debug` — Show raw data sources

**Control**
• `/ai off` — Slash commands only (bot stays silent)
• `/ai quiet` — Slash commands + @mentions
• `/ai active` — Full natural language (default)
• `/private` — See what Memu protects
• Current mode: {mode_display.get(current_mode, '🔊 Active')}

**Other**
• `/summarize` — AI summary of recent chat
• `/help` — Show this message

💡 You can also just talk to me naturally! Try:
• "What's happening tomorrow?"
• "Add milk and eggs to the list"
• "Remind me to call the dentist Friday"
• "What have we been doing on Saturdays?"

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

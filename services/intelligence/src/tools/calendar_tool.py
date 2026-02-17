"""
Calendar Tool for Memu Intelligence Service

Provides CalDAV integration with Baikal for family calendar management.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from zoneinfo import ZoneInfo
import asyncio
from functools import partial

import caldav
from icalendar import Calendar, Event
import dateparser

from config import Config

logger = logging.getLogger("memu.calendar")


class CalendarManager:
    """
    Manages family calendar via CalDAV (Baikal).

    Provides methods to:
    - Get events for a date range
    - Add new events
    - Find free time slots
    """

    def __init__(self):
        self.caldav_url = Config.CALDAV_URL
        self.username = Config.CALDAV_USERNAME
        self.password = Config.CALDAV_PASSWORD
        self.timezone = ZoneInfo(Config.TIMEZONE)
        self._client: Optional[caldav.DAVClient] = None
        self._calendar: Optional[caldav.Calendar] = None

    def _get_client(self) -> caldav.DAVClient:
        """Get or create CalDAV client."""
        if self._client is None:
            self._client = caldav.DAVClient(
                url=self.caldav_url,
                username=self.username,
                password=self.password
            )
        return self._client

    def _get_calendar(self) -> Optional[caldav.Calendar]:
        """Get the family calendar (first available or create one)."""
        if self._calendar is not None:
            return self._calendar

        try:
            client = self._get_client()
            logger.info(f"Connecting to CalDAV: {self.caldav_url} as {self.username}")
            
            principal = None
            try:
                principal = client.principal()
            except Exception as e:
                logger.warning(f"Auto-discovery failed: {e}. Trying direct principal path...")
            
            # Fallback for Baikal if auto-discovery fails
            if not principal:
                # Construct explicit principal URL for Baikal
                # Format: /calendar/dav.php/principals/users/USERNAME/
                base = self.caldav_url.rstrip('/')
                principal_url = f"{base}/principals/users/{self.username}/"
                logger.info(f"Attempting direct principal URL: {principal_url}")
                # Fix: explicit keyword argument 'url' required
                principal = client.principal(url=principal_url)

            calendars = principal.calendars()

            if calendars:
                # Use the first calendar (typically "default" or "Family")
                self._calendar = calendars[0]
                logger.info(f"Using calendar: {self._calendar.name} (URL: {self._calendar.url})")
            else:
                # Create a new calendar
                self._calendar = principal.make_calendar(name="Family")
                logger.info("Created new 'Family' calendar")

            return self._calendar
        except Exception as e:
            logger.error(f"Failed to get calendar: {e}")
            return None

    def _sync_get_events(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """Synchronous implementation of get_events."""
        calendar = self._get_calendar()
        if not calendar:
            return []

        events = []
        try:
            # Search for events in date range
            results = calendar.search(
                start=start,
                end=end,
                event=True,
                expand=False
            )

            for event in results:
                try:
                    ical = Calendar.from_ical(event.data)
                    for component in ical.walk():
                        if component.name == "VEVENT":
                            events.append(self._parse_vevent(component))
                except Exception as e:
                    logger.warning(f"Failed to parse event: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to fetch events: {e}")

        # Sort by start time
        events.sort(key=lambda x: x['start'])
        return events

    def _parse_vevent(self, vevent) -> Dict[str, Any]:
        """Parse a VEVENT component into a dictionary."""
        dt_start = vevent.get('dtstart')
        dt_end = vevent.get('dtend')

        # Handle date vs datetime
        start = dt_start.dt if dt_start else None
        end = dt_end.dt if dt_end else None

        # Convert to datetime if needed
        if start and not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time()).replace(tzinfo=self.timezone)
        if end and not isinstance(end, datetime):
            end = datetime.combine(end, datetime.min.time()).replace(tzinfo=self.timezone)

        # Ensure timezone
        if start and start.tzinfo is None:
            start = start.replace(tzinfo=self.timezone)
        if end and end.tzinfo is None:
            end = end.replace(tzinfo=self.timezone)

        return {
            'summary': str(vevent.get('summary', 'Untitled')),
            'start': start,
            'end': end,
            'location': str(vevent.get('location', '')),
            'description': str(vevent.get('description', '')),
            'uid': str(vevent.get('uid', '')),
            'all_day': not isinstance(dt_start.dt, datetime) if dt_start else False
        }

    async def get_events(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events within a date range.

        Args:
            start: Start of range (defaults to today 00:00)
            end: End of range (defaults to start + 7 days)

        Returns:
            List of event dictionaries with keys:
            - summary: Event title
            - start: datetime
            - end: datetime
            - location: str
            - description: str
            - all_day: bool
        """
        now = datetime.now(self.timezone)

        if start is None:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if end is None:
            end = start + timedelta(days=7)

        # Ensure timezone
        if start.tzinfo is None:
            start = start.replace(tzinfo=self.timezone)
        if end.tzinfo is None:
            end = end.replace(tzinfo=self.timezone)

        # Run sync operation in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._sync_get_events, start, end)
        )

    def _sync_search_events(self, query: str, months_back: int = 12) -> List[Dict[str, Any]]:
        """Synchronous implementation of search_events."""
        calendar = self._get_calendar()
        if not calendar:
            return []

        now = datetime.now(self.timezone)
        start = now - timedelta(days=months_back * 30)
        end = now + timedelta(days=90)  # Also search 3 months ahead

        events = []
        try:
            results = calendar.search(
                start=start,
                end=end,
                event=True,
                expand=False
            )

            query_lower = query.lower()
            for event in results:
                try:
                    ical = Calendar.from_ical(event.data)
                    for component in ical.walk():
                        if component.name == "VEVENT":
                            parsed = self._parse_vevent(component)
                            searchable = f"{parsed['summary']} {parsed['description']} {parsed['location']}".lower()
                            if query_lower in searchable:
                                events.append(parsed)
                except Exception as e:
                    logger.warning(f"Failed to parse event during search: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to search events: {e}")

        events.sort(key=lambda x: x['start'])
        return events

    async def search_events(
        self,
        query: str,
        months_back: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Search calendar events by keyword across a wide date range.

        Args:
            query: Search term to match against event summary, description, or location
            months_back: How many months back to search (default 12)

        Returns:
            List of matching event dictionaries
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._sync_search_events, query, months_back)
        )

    def _sync_add_event(
        self,
        summary: str,
        dt_start: datetime,
        dt_end: Optional[datetime],
        location: str,
        description: str
    ) -> Optional[str]:
        """Synchronous implementation of add_event."""
        calendar = self._get_calendar()
        if not calendar:
            return None

        try:
            # Create iCalendar event
            cal = Calendar()
            cal.add('prodid', '-//Memu Family Calendar//memu.digital//')
            cal.add('version', '2.0')

            event = Event()
            event.add('summary', summary)
            event.add('dtstart', dt_start)
            event.add('dtend', dt_end)

            if location:
                event.add('location', location)
            if description:
                event.add('description', description)

            # Add UID
            import uuid
            uid = f"{uuid.uuid4()}@memu.digital"
            event.add('uid', uid)
            event.add('dtstamp', datetime.now(self.timezone))

            cal.add_component(event)

            # Save to CalDAV
            calendar.save_event(cal.to_ical().decode('utf-8'))
            logger.info(f"Created event: {summary} at {dt_start}")

            return uid

        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return None

    async def add_event(
        self,
        summary: str,
        dt_start: datetime,
        dt_end: Optional[datetime] = None,
        location: str = "",
        description: str = ""
    ) -> Optional[str]:
        """
        Add a new event to the family calendar.

        Args:
            summary: Event title
            dt_start: Start time
            dt_end: End time (defaults to start + 1 hour)
            location: Event location
            description: Event description

        Returns:
            Event UID if successful, None otherwise
        """
        # Ensure timezone
        if dt_start.tzinfo is None:
            dt_start = dt_start.replace(tzinfo=self.timezone)

        if dt_end is None:
            dt_end = dt_start + timedelta(hours=1)
        elif dt_end.tzinfo is None:
            dt_end = dt_end.replace(tzinfo=self.timezone)

        # Run sync operation in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._sync_add_event, summary, dt_start, dt_end, location, description)
        )

    async def get_today_events(self) -> List[Dict[str, Any]]:
        """Get all events for today."""
        now = datetime.now(self.timezone)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return await self.get_events(start, end)

    async def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get events for the next N days."""
        now = datetime.now(self.timezone)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=days)
        return await self.get_events(start, end)

    async def find_free_slots(
        self,
        date: Optional[datetime] = None,
        min_duration_minutes: int = 30,
        working_hours: tuple = (9, 17)
    ) -> List[Dict[str, Any]]:
        """
        Find free time slots on a given date.

        Args:
            date: The date to check (defaults to today)
            min_duration_minutes: Minimum slot duration
            working_hours: Tuple of (start_hour, end_hour)

        Returns:
            List of free slots with 'start' and 'end' datetimes
        """
        if date is None:
            date = datetime.now(self.timezone)

        # Get the day's boundaries
        day_start = date.replace(
            hour=working_hours[0], minute=0, second=0, microsecond=0,
            tzinfo=self.timezone
        )
        day_end = date.replace(
            hour=working_hours[1], minute=0, second=0, microsecond=0,
            tzinfo=self.timezone
        )

        # Get events for the day
        events = await self.get_events(day_start, day_end)

        # Find gaps
        free_slots = []
        current_time = day_start

        for event in events:
            event_start = event['start']
            event_end = event['end']

            # Skip all-day events for slot calculation
            if event.get('all_day'):
                continue

            # If there's a gap before this event
            if event_start > current_time:
                gap_minutes = (event_start - current_time).total_seconds() / 60
                if gap_minutes >= min_duration_minutes:
                    free_slots.append({
                        'start': current_time,
                        'end': event_start,
                        'duration_minutes': int(gap_minutes)
                    })

            # Move current time to after this event
            if event_end and event_end > current_time:
                current_time = event_end

        # Check for gap after last event
        if current_time < day_end:
            gap_minutes = (day_end - current_time).total_seconds() / 60
            if gap_minutes >= min_duration_minutes:
                free_slots.append({
                    'start': current_time,
                    'end': day_end,
                    'duration_minutes': int(gap_minutes)
                })

        return free_slots

    def format_event(self, event: Dict[str, Any]) -> str:
        """Format an event for display in chat."""
        start = event['start']
        end = event['end']
        summary = event['summary']

        if event.get('all_day'):
            time_str = "All day"
        else:
            time_str = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"

        location = f" @ {event['location']}" if event.get('location') else ""

        return f"{time_str}: {summary}{location}"

    def format_events_list(self, events: List[Dict[str, Any]]) -> str:
        """Format a list of events for display."""
        if not events:
            return "No events scheduled."

        lines = []
        current_date = None

        for event in events:
            event_date = event['start'].date()

            # Add date header if new day
            if event_date != current_date:
                current_date = event_date
                lines.append(f"\n**{event_date.strftime('%A, %B %d')}**")

            lines.append(f"  {self.format_event(event)}")

        return "\n".join(lines)

    async def is_available(self) -> bool:
        """Check if the calendar service is available."""
        try:
            client = self._get_client()
            principal = client.principal()
            return principal is not None
        except Exception as e:
            logger.warning(f"Calendar service unavailable: {e}")
            return False

"""
Tests for the CalendarManager tool.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from tools.calendar_tool import CalendarManager


@pytest.fixture
def calendar_manager():
    """Create a CalendarManager instance with mocked config."""
    with patch('tools.calendar_tool.Config') as mock_config:
        mock_config.CALDAV_URL = "http://calendar/dav.php"
        mock_config.CALDAV_USERNAME = "test_user"
        mock_config.CALDAV_PASSWORD = "test_pass"
        mock_config.TIMEZONE = "Europe/London"
        manager = CalendarManager()
        return manager


@pytest.fixture
def mock_vevent():
    """Create a mock VEVENT component."""
    tz = ZoneInfo("Europe/London")
    vevent = MagicMock()

    mock_dtstart = MagicMock()
    mock_dtstart.dt = datetime(2025, 3, 15, 14, 0, tzinfo=tz)

    mock_dtend = MagicMock()
    mock_dtend.dt = datetime(2025, 3, 15, 15, 0, tzinfo=tz)

    vevent.get.side_effect = lambda key, default='': {
        'dtstart': mock_dtstart,
        'dtend': mock_dtend,
        'summary': 'Team Meeting',
        'location': 'Office',
        'description': 'Weekly sync',
        'uid': 'test-uid-123'
    }.get(key, default)

    return vevent


class TestCalendarManagerParsing:
    """Tests for parsing calendar events."""

    def test_parse_vevent_basic(self, calendar_manager, mock_vevent):
        """Test parsing a basic VEVENT."""
        result = calendar_manager._parse_vevent(mock_vevent)

        assert result['summary'] == 'Team Meeting'
        assert result['location'] == 'Office'
        assert result['description'] == 'Weekly sync'
        assert result['start'].hour == 14
        assert result['end'].hour == 15

    def test_parse_vevent_all_day(self, calendar_manager):
        """Test parsing an all-day event."""
        tz = ZoneInfo("Europe/London")
        vevent = MagicMock()

        mock_dtstart = MagicMock()
        mock_dtstart.dt = datetime(2025, 3, 15).date()  # Date, not datetime

        mock_dtend = MagicMock()
        mock_dtend.dt = datetime(2025, 3, 16).date()

        vevent.get.side_effect = lambda key, default='': {
            'dtstart': mock_dtstart,
            'dtend': mock_dtend,
            'summary': 'Holiday',
            'location': '',
            'description': '',
            'uid': 'test-uid-456'
        }.get(key, default)

        result = calendar_manager._parse_vevent(vevent)

        assert result['summary'] == 'Holiday'
        assert result['all_day'] is True


class TestCalendarManagerFormatting:
    """Tests for formatting calendar events."""

    def test_format_event_basic(self, calendar_manager):
        """Test formatting a basic event."""
        tz = ZoneInfo("Europe/London")
        event = {
            'summary': 'Dentist Appointment',
            'start': datetime(2025, 3, 15, 10, 30, tzinfo=tz),
            'end': datetime(2025, 3, 15, 11, 30, tzinfo=tz),
            'location': 'High Street',
            'all_day': False
        }

        result = calendar_manager.format_event(event)

        assert '10:30-11:30' in result
        assert 'Dentist Appointment' in result
        assert 'High Street' in result

    def test_format_event_all_day(self, calendar_manager):
        """Test formatting an all-day event."""
        tz = ZoneInfo("Europe/London")
        event = {
            'summary': 'School Holiday',
            'start': datetime(2025, 3, 15, tzinfo=tz),
            'end': datetime(2025, 3, 16, tzinfo=tz),
            'location': '',
            'all_day': True
        }

        result = calendar_manager.format_event(event)

        assert 'All day' in result
        assert 'School Holiday' in result

    def test_format_events_list_empty(self, calendar_manager):
        """Test formatting an empty events list."""
        result = calendar_manager.format_events_list([])
        assert result == "No events scheduled."

    def test_format_events_list_multiple(self, calendar_manager):
        """Test formatting multiple events."""
        tz = ZoneInfo("Europe/London")
        events = [
            {
                'summary': 'Morning Meeting',
                'start': datetime(2025, 3, 15, 9, 0, tzinfo=tz),
                'end': datetime(2025, 3, 15, 10, 0, tzinfo=tz),
                'location': '',
                'all_day': False
            },
            {
                'summary': 'Lunch',
                'start': datetime(2025, 3, 15, 12, 0, tzinfo=tz),
                'end': datetime(2025, 3, 15, 13, 0, tzinfo=tz),
                'location': 'Cafe',
                'all_day': False
            }
        ]

        result = calendar_manager.format_events_list(events)

        assert 'March 15' in result
        assert 'Morning Meeting' in result
        assert 'Lunch' in result
        assert 'Cafe' in result


class TestCalendarManagerAsync:
    """Tests for async calendar operations."""

    @pytest.mark.asyncio
    async def test_get_events_uses_executor(self, calendar_manager):
        """Test that get_events runs sync code in executor."""
        with patch.object(calendar_manager, '_sync_get_events') as mock_sync:
            mock_sync.return_value = []

            result = await calendar_manager.get_events()

            assert result == []

    @pytest.mark.asyncio
    async def test_add_event_uses_executor(self, calendar_manager):
        """Test that add_event runs sync code in executor."""
        with patch.object(calendar_manager, '_sync_add_event') as mock_sync:
            mock_sync.return_value = 'test-uid-789'
            tz = ZoneInfo("Europe/London")

            result = await calendar_manager.add_event(
                summary='Test Event',
                dt_start=datetime(2025, 3, 15, 14, 0, tzinfo=tz)
            )

            assert result == 'test-uid-789'

    @pytest.mark.asyncio
    async def test_get_today_events(self, calendar_manager):
        """Test getting today's events."""
        tz = ZoneInfo("Europe/London")
        mock_events = [
            {
                'summary': 'Today Event',
                'start': datetime.now(tz),
                'end': datetime.now(tz) + timedelta(hours=1),
                'location': '',
                'all_day': False
            }
        ]

        with patch.object(calendar_manager, 'get_events', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_events

            result = await calendar_manager.get_today_events()

            assert len(result) == 1
            assert result[0]['summary'] == 'Today Event'

    @pytest.mark.asyncio
    async def test_is_available_success(self, calendar_manager):
        """Test availability check when calendar is available."""
        mock_principal = MagicMock()

        with patch.object(calendar_manager, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.principal.return_value = mock_principal
            mock_get_client.return_value = mock_client

            result = await calendar_manager.is_available()

            assert result is True

    @pytest.mark.asyncio
    async def test_is_available_failure(self, calendar_manager):
        """Test availability check when calendar is unavailable."""
        with patch.object(calendar_manager, '_get_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")

            result = await calendar_manager.is_available()

            assert result is False


class TestFindFreeSlots:
    """Tests for finding free time slots."""

    @pytest.mark.asyncio
    async def test_find_free_slots_empty_day(self, calendar_manager):
        """Test finding free slots on a day with no events."""
        with patch.object(calendar_manager, 'get_events', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            tz = ZoneInfo("Europe/London")
            test_date = datetime(2025, 3, 15, 10, 0, tzinfo=tz)

            result = await calendar_manager.find_free_slots(
                date=test_date,
                working_hours=(9, 17)
            )

            # Should have one big free slot from 9am to 5pm
            assert len(result) == 1
            assert result[0]['duration_minutes'] == 8 * 60  # 8 hours

    @pytest.mark.asyncio
    async def test_find_free_slots_with_events(self, calendar_manager):
        """Test finding free slots around scheduled events."""
        tz = ZoneInfo("Europe/London")
        events = [
            {
                'summary': 'Meeting',
                'start': datetime(2025, 3, 15, 10, 0, tzinfo=tz),
                'end': datetime(2025, 3, 15, 11, 0, tzinfo=tz),
                'all_day': False
            },
            {
                'summary': 'Lunch',
                'start': datetime(2025, 3, 15, 12, 0, tzinfo=tz),
                'end': datetime(2025, 3, 15, 13, 0, tzinfo=tz),
                'all_day': False
            }
        ]

        with patch.object(calendar_manager, 'get_events', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = events
            test_date = datetime(2025, 3, 15, 10, 0, tzinfo=tz)

            result = await calendar_manager.find_free_slots(
                date=test_date,
                working_hours=(9, 17)
            )

            # Should have slots: 9-10, 11-12, 13-17
            assert len(result) == 3

            # First slot: 9:00 - 10:00 (1 hour)
            assert result[0]['duration_minutes'] == 60

            # Second slot: 11:00 - 12:00 (1 hour)
            assert result[1]['duration_minutes'] == 60

            # Third slot: 13:00 - 17:00 (4 hours)
            assert result[2]['duration_minutes'] == 4 * 60

    @pytest.mark.asyncio
    async def test_find_free_slots_ignores_all_day(self, calendar_manager):
        """Test that all-day events don't block time slots."""
        tz = ZoneInfo("Europe/London")
        events = [
            {
                'summary': 'Holiday Reminder',
                'start': datetime(2025, 3, 15, 0, 0, tzinfo=tz),
                'end': datetime(2025, 3, 16, 0, 0, tzinfo=tz),
                'all_day': True
            }
        ]

        with patch.object(calendar_manager, 'get_events', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = events
            test_date = datetime(2025, 3, 15, 10, 0, tzinfo=tz)

            result = await calendar_manager.find_free_slots(
                date=test_date,
                working_hours=(9, 17)
            )

            # All-day event should not block slots
            assert len(result) == 1
            assert result[0]['duration_minutes'] == 8 * 60

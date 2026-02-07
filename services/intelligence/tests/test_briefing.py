"""
Tests for the Morning Briefing Agent.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from zoneinfo import ZoneInfo

from agents.briefing import MorningBriefingAgent


@pytest.fixture
def mock_bot():
    """Create a mock MemuBot instance."""
    bot = MagicMock()
    bot.send_text = AsyncMock()
    bot.brain = MagicMock()
    bot.brain.generate = AsyncMock(return_value="Good morning! Here's your briefing...")
    bot.memory = MagicMock()
    bot.memory.get_list = AsyncMock(return_value=[])
    bot.calendar = MagicMock()
    bot.calendar.get_today_events = AsyncMock(return_value=[])
    return bot


@pytest.fixture
def briefing_agent(mock_bot):
    """Create a MorningBriefingAgent with mocked bot."""
    with patch('agents.briefing.Config') as mock_config:
        mock_config.TIMEZONE = "Europe/London"
        mock_config.WEATHER_API_KEY = ""
        mock_config.IMMICH_API_KEY = ""
        mock_config.PRIMARY_ROOM_ID = "!test:memu.local"
        agent = MorningBriefingAgent(mock_bot)
        return agent


class TestGatherCalendar:
    """Tests for calendar data gathering."""

    @pytest.mark.asyncio
    async def test_gather_calendar_with_events(self, briefing_agent, mock_bot):
        """Test gathering calendar with events."""
        tz = ZoneInfo("Europe/London")
        mock_events = [
            {
                'summary': 'Team Meeting',
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
        mock_bot.calendar.get_today_events.return_value = mock_events

        result = await briefing_agent.gather_calendar()

        assert result['available'] is True
        assert result['count'] == 2
        assert len(result['events']) == 2

    @pytest.mark.asyncio
    async def test_gather_calendar_empty(self, briefing_agent, mock_bot):
        """Test gathering calendar with no events."""
        mock_bot.calendar.get_today_events.return_value = []

        result = await briefing_agent.gather_calendar()

        assert result['available'] is True
        assert result['count'] == 0

    @pytest.mark.asyncio
    async def test_gather_calendar_error(self, briefing_agent, mock_bot):
        """Test handling calendar errors gracefully."""
        mock_bot.calendar.get_today_events.side_effect = Exception("Connection failed")

        result = await briefing_agent.gather_calendar()

        assert result['available'] is False


class TestGatherWeather:
    """Tests for weather data gathering."""

    @pytest.mark.asyncio
    async def test_gather_weather_no_api_key(self, briefing_agent):
        """Test weather gathering without API key."""
        result = await briefing_agent.gather_weather()
        assert result['available'] is False

    @pytest.mark.asyncio
    async def test_gather_weather_success(self, mock_bot):
        """Test successful weather API call."""
        with patch('agents.briefing.Config') as mock_config:
            mock_config.TIMEZONE = "Europe/London"
            mock_config.WEATHER_API_KEY = "test_key"
            mock_config.WEATHER_CITY = "London"
            mock_config.WEATHER_COUNTRY = "UK"
            mock_config.IMMICH_API_KEY = ""
            mock_config.PRIMARY_ROOM_ID = ""

            agent = MorningBriefingAgent(mock_bot)

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'main': {'temp': 15.5, 'feels_like': 14.2, 'humidity': 65},
                'weather': [{'description': 'partly cloudy', 'icon': '02d'}]
            }
            mock_response.raise_for_status = MagicMock()

            with patch('httpx.AsyncClient') as mock_client:
                mock_context = AsyncMock()
                mock_context.get = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_context

                result = await agent.gather_weather()

                assert result['available'] is True
                assert result['temp'] == 16  # Rounded
                assert result['description'] == 'partly cloudy'
                assert result['icon'] == '⛅'


class TestGatherShoppingList:
    """Tests for shopping list gathering."""

    @pytest.mark.asyncio
    async def test_gather_shopping_with_items(self, mock_bot):
        """Test gathering shopping list with items."""
        with patch('agents.briefing.Config') as mock_config:
            mock_config.TIMEZONE = "Europe/London"
            mock_config.WEATHER_API_KEY = ""
            mock_config.IMMICH_API_KEY = ""
            mock_config.PRIMARY_ROOM_ID = "!test:memu.local"

            mock_bot.memory.get_list.return_value = [
                {'item': 'Milk', 'completed': False},
                {'item': 'Bread', 'completed': False},
                {'item': 'Eggs', 'completed': True}
            ]

            agent = MorningBriefingAgent(mock_bot)
            result = await agent.gather_shopping_list()

            assert result['available'] is True
            assert result['active_count'] == 2
            assert 'Milk' in result['items']
            assert 'Bread' in result['items']

    @pytest.mark.asyncio
    async def test_gather_shopping_no_room(self, mock_bot):
        """Test shopping list without room configured."""
        with patch('agents.briefing.Config') as mock_config:
            mock_config.TIMEZONE = "Europe/London"
            mock_config.WEATHER_API_KEY = ""
            mock_config.IMMICH_API_KEY = ""
            mock_config.PRIMARY_ROOM_ID = ""

            agent = MorningBriefingAgent(mock_bot)
            result = await agent.gather_shopping_list()

            assert result['available'] is False


class TestBuildPrompt:
    """Tests for briefing prompt building."""

    def test_build_prompt_full(self, briefing_agent):
        """Test building prompt with all data available."""
        tz = ZoneInfo("Europe/London")
        data = {
            'timestamp': datetime(2025, 3, 15, 7, 0, tzinfo=tz),
            'calendar': {
                'available': True,
                'count': 2,
                'events': [
                    {'summary': 'Meeting', 'start': datetime(2025, 3, 15, 10, 0, tzinfo=tz), 'all_day': False},
                    {'summary': 'Lunch', 'start': datetime(2025, 3, 15, 12, 0, tzinfo=tz), 'all_day': False}
                ]
            },
            'weather': {
                'available': True,
                'icon': '☀️',
                'description': 'sunny',
                'temp': 18,
                'feels_like': 17
            },
            'memories': {
                'available': True,
                'total_count': 5,
                'by_year': {1: 2, 3: 3}
            },
            'shopping': {
                'available': True,
                'active_count': 3,
                'items': ['Milk', 'Bread', 'Eggs']
            }
        }

        prompt = briefing_agent.build_briefing_prompt(data)

        assert 'Saturday, March 15, 2025' in prompt
        assert 'Meeting' in prompt
        assert 'Lunch' in prompt
        assert 'sunny' in prompt
        assert '18°C' in prompt
        assert 'Photo memories' in prompt
        assert 'Shopping list: 3 items' in prompt

    def test_build_prompt_minimal(self, briefing_agent):
        """Test building prompt with minimal data."""
        tz = ZoneInfo("Europe/London")
        data = {
            'timestamp': datetime(2025, 3, 15, 7, 0, tzinfo=tz),
            'calendar': {'available': False, 'count': 0, 'events': []},
            'weather': {'available': False},
            'memories': {'available': False},
            'shopping': {'available': False}
        }

        prompt = briefing_agent.build_briefing_prompt(data)

        assert 'Saturday, March 15, 2025' in prompt
        assert 'No events scheduled' in prompt


class TestFallbackBriefing:
    """Tests for fallback briefing generation."""

    def test_fallback_with_events(self, briefing_agent):
        """Test fallback briefing with calendar events."""
        tz = ZoneInfo("Europe/London")
        data = {
            'timestamp': datetime(2025, 3, 15, 7, 0, tzinfo=tz),
            'calendar': {'available': True, 'count': 3, 'events': []},
            'weather': {'available': True, 'icon': '☀️', 'temp': 20, 'description': 'clear'},
            'memories': {'available': True, 'total_count': 5},
            'shopping': {'available': True, 'active_count': 2}
        }

        result = briefing_agent._fallback_briefing(data)

        assert 'Good morning' in result
        assert '3 event(s)' in result
        assert '20°C' in result
        assert '5 photo memories' in result
        assert '2 items' in result


class TestDeliver:
    """Tests for briefing delivery."""

    @pytest.mark.asyncio
    async def test_deliver_success(self, briefing_agent, mock_bot):
        """Test successful briefing delivery."""
        with patch.object(briefing_agent, 'gather_all', new_callable=AsyncMock) as mock_gather:
            tz = ZoneInfo("Europe/London")
            mock_gather.return_value = {
                'timestamp': datetime(2025, 3, 15, 7, 0, tzinfo=tz),
                'calendar': {'available': True, 'count': 0, 'events': []},
                'weather': {'available': False},
                'memories': {'available': False},
                'shopping': {'available': False}
            }

            result = await briefing_agent.deliver("!test:memu.local")

            assert result is True
            mock_bot.send_text.assert_called_once()
            call_args = mock_bot.send_text.call_args
            assert "!test:memu.local" == call_args[0][0]
            assert "Morning Briefing" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_deliver_no_room(self, mock_bot):
        """Test delivery without room configured."""
        with patch('agents.briefing.Config') as mock_config:
            mock_config.TIMEZONE = "Europe/London"
            mock_config.WEATHER_API_KEY = ""
            mock_config.IMMICH_API_KEY = ""
            mock_config.PRIMARY_ROOM_ID = ""

            agent = MorningBriefingAgent(mock_bot)
            result = await agent.deliver()

            assert result is False
            mock_bot.send_text.assert_not_called()


class TestWeatherEmoji:
    """Tests for weather emoji mapping."""

    def test_weather_emoji_sun(self, briefing_agent):
        """Test sunny weather emoji."""
        assert briefing_agent._weather_emoji('01d') == '☀️'

    def test_weather_emoji_rain(self, briefing_agent):
        """Test rainy weather emoji."""
        assert briefing_agent._weather_emoji('10d') == '🌦️'

    def test_weather_emoji_unknown(self, briefing_agent):
        """Test unknown weather code fallback."""
        assert briefing_agent._weather_emoji('99x') == '🌤️'

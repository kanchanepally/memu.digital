"""
Morning Briefing Agent for Memu Intelligence Service

Delivers a warm, personalized morning briefing to the family chat room.
Synthesizes: Calendar, Weather, News, Photos ("On This Day"), and Shopping List.
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from zoneinfo import ZoneInfo
import httpx

from config import Config

if TYPE_CHECKING:
    from bot import MemuBot

logger = logging.getLogger("memu.briefing")


class MorningBriefingAgent:
    """
    Generates and delivers morning briefings to the family.

    The briefing includes:
    - Today's calendar events
    - Current weather
    - "On This Day" photo memories
    - Shopping list status
    """

    def __init__(self, bot: "MemuBot"):
        self.bot = bot
        self.timezone = ZoneInfo(Config.TIMEZONE)

    async def gather_calendar(self) -> Dict[str, Any]:
        """Get today's calendar events."""
        try:
            events = await self.bot.calendar.get_today_events()
            return {
                'available': True,
                'count': len(events),
                'events': events[:5],  # Limit to first 5 for briefing
                'has_more': len(events) > 5
            }
        except Exception as e:
            logger.warning(f"Failed to get calendar: {e}")
            return {'available': False, 'count': 0, 'events': []}

    async def gather_weather(self) -> Dict[str, Any]:
        """Get current weather from OpenWeatherMap."""
        if not Config.WEATHER_API_KEY:
            return {'available': False}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    'q': f"{Config.WEATHER_CITY},{Config.WEATHER_COUNTRY}",
                    'appid': Config.WEATHER_API_KEY,
                    'units': 'metric'
                }
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return {
                    'available': True,
                    'city': data.get('name', Config.WEATHER_CITY),
                    'temp': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'description': data['weather'][0]['description'],
                    'icon': self._weather_emoji(data['weather'][0]['icon']),
                    'humidity': data['main']['humidity']
                }
        except Exception as e:
            logger.warning(f"Failed to get weather: {e}")
            return {'available': False}

    def _weather_emoji(self, icon_code: str) -> str:
        """Convert OpenWeatherMap icon code to emoji."""
        mapping = {
            '01d': '☀️', '01n': '🌙',  # Clear
            '02d': '⛅', '02n': '☁️',  # Few clouds
            '03d': '☁️', '03n': '☁️',  # Scattered clouds
            '04d': '☁️', '04n': '☁️',  # Broken clouds
            '09d': '🌧️', '09n': '🌧️',  # Shower rain
            '10d': '🌦️', '10n': '🌧️',  # Rain
            '11d': '⛈️', '11n': '⛈️',  # Thunderstorm
            '13d': '🌨️', '13n': '🌨️',  # Snow
            '50d': '🌫️', '50n': '🌫️',  # Mist
        }
        return mapping.get(icon_code, '🌤️')

    async def gather_news(self) -> Dict[str, Any]:
        """Get top headlines from configured RSS feeds."""
        feeds_str = Config.BRIEFING_NEWS_FEEDS
        if not feeds_str or not feeds_str.strip():
            return {'available': False}

        feed_urls = [u.strip() for u in feeds_str.split(',') if u.strip()]
        if not feed_urls:
            return {'available': False}

        headlines: List[Dict[str, str]] = []
        max_count = Config.BRIEFING_NEWS_COUNT

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                for feed_url in feed_urls:
                    if len(headlines) >= max_count:
                        break
                    try:
                        response = await client.get(feed_url)
                        if response.status_code != 200:
                            continue
                        root = ET.fromstring(response.text)
                        # Standard RSS 2.0 parsing
                        for item in root.iter('item'):
                            if len(headlines) >= max_count:
                                break
                            title_el = item.find('title')
                            if title_el is not None and title_el.text:
                                headlines.append({
                                    'title': title_el.text.strip()
                                })
                    except Exception as e:
                        logger.debug(f"Failed to fetch feed {feed_url}: {e}")
                        continue

            return {
                'available': len(headlines) > 0,
                'headlines': headlines
            }

        except Exception as e:
            logger.warning(f"Failed to get news: {e}")
            return {'available': False}

    async def gather_memories(self) -> Dict[str, Any]:
        """Get 'On This Day' photos from Immich."""
        if not Config.IMMICH_API_KEY:
            return {'available': False}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Immich API endpoint for memories/on-this-day
                url = f"{Config.IMMICH_API_URL}/api/asset/memory-lane"
                headers = {'x-api-key': Config.IMMICH_API_KEY}

                today = datetime.now(self.timezone)
                params = {
                    'day': today.day,
                    'month': today.month
                }

                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    # Group by year
                    memories_by_year = {}
                    for memory in data:
                        year = memory.get('yearsAgo', 0)
                        if year not in memories_by_year:
                            memories_by_year[year] = 0
                        memories_by_year[year] += 1

                    return {
                        'available': True,
                        'total_count': len(data),
                        'by_year': memories_by_year
                    }
                else:
                    return {'available': False}

        except Exception as e:
            logger.warning(f"Failed to get memories: {e}")
            return {'available': False}

    async def gather_shopping_list(self) -> Dict[str, Any]:
        """Get shopping list status."""
        try:
            # We need a room_id to get the list, use primary room
            if not Config.PRIMARY_ROOM_ID:
                return {'available': False}

            items = await self.bot.memory.get_list(Config.PRIMARY_ROOM_ID)
            active = [i for i in items if not i.get('completed')]

            return {
                'available': True,
                'active_count': len(active),
                'items': [i['item'] for i in active[:3]]  # First 3 items
            }
        except Exception as e:
            logger.warning(f"Failed to get shopping list: {e}")
            return {'available': False}

    async def gather_all(self) -> Dict[str, Any]:
        """Gather all data sources for the briefing."""
        return {
            'calendar': await self.gather_calendar(),
            'weather': await self.gather_weather(),
            'news': await self.gather_news(),
            'memories': await self.gather_memories(),
            'shopping': await self.gather_shopping_list(),
            'timestamp': datetime.now(self.timezone)
        }

    def build_briefing_prompt(self, data: Dict[str, Any]) -> str:
        """Build the prompt for Ollama to generate the briefing."""
        parts = []

        # Date context
        now = data['timestamp']
        parts.append(f"Today is {now.strftime('%A, %B %d, %Y')}.")

        # Calendar
        cal = data['calendar']
        if cal['available'] and cal['count'] > 0:
            events_text = []
            for e in cal['events']:
                time_str = e['start'].strftime('%H:%M') if not e.get('all_day') else 'All day'
                events_text.append(f"- {time_str}: {e['summary']}")
            parts.append(f"Today's schedule ({cal['count']} events):\n" + "\n".join(events_text))
        else:
            parts.append("No events scheduled for today.")

        # Weather
        weather = data['weather']
        if weather['available']:
            parts.append(
                f"Weather in {weather.get('city', Config.WEATHER_CITY)}: "
                f"{weather['icon']} {weather['description']}, "
                f"{weather['temp']}°C (feels like {weather['feels_like']}°C)"
            )

        # News
        news = data.get('news', {})
        if news.get('available') and news.get('headlines'):
            news_items = [f"- {h['title']}" for h in news['headlines']]
            parts.append(f"Today's headlines:\n" + "\n".join(news_items))

        # Memories
        memories = data['memories']
        if memories['available'] and memories['total_count'] > 0:
            years_text = []
            for years_ago, count in sorted(memories['by_year'].items()):
                if years_ago == 1:
                    years_text.append(f"{count} from last year")
                else:
                    years_text.append(f"{count} from {years_ago} years ago")
            parts.append(f"Photo memories from this day: {', '.join(years_text)}")

        # Shopping
        shopping = data['shopping']
        if shopping['available'] and shopping['active_count'] > 0:
            items_preview = ", ".join(shopping['items'])
            if shopping['active_count'] > 3:
                items_preview += f" (+{shopping['active_count'] - 3} more)"
            parts.append(f"Shopping list: {shopping['active_count']} items ({items_preview})")

        return "\n\n".join(parts)

    async def generate_briefing(self, data: Dict[str, Any]) -> str:
        """Generate the morning briefing using Ollama."""
        context = self.build_briefing_prompt(data)

        system_prompt = """You are a warm, helpful Family Chief of Staff.
Write a brief, friendly morning briefing (3-4 sentences max) for the family.
Be conversational and encouraging. Highlight the most important things for the day.
If there are photo memories, mention them warmly.
Keep it concise - this is a quick morning update, not a detailed report.
Use a friendly emoji or two where appropriate.
IMPORTANT: Only describe weather using the EXACT data provided (temperature, description).
Do NOT invent weather details or suggest enjoying weather that contradicts the data.
If it says 'overcast clouds' and 5°C, do NOT say 'enjoy the sunshine'."""

        prompt = f"""Based on this information, write a warm morning briefing:

{context}

Morning briefing:"""

        try:
            briefing = await self.bot.brain.generate(prompt, system_prompt=system_prompt)
            if briefing:
                return briefing
        except Exception as e:
            logger.error(f"Failed to generate briefing: {e}")

        # Fallback: simple formatted briefing if AI fails
        return self._fallback_briefing(data)

    def _fallback_briefing(self, data: Dict[str, Any]) -> str:
        """Generate a simple briefing without AI."""
        now = data['timestamp']
        lines = [f"☀️ Good morning! It's {now.strftime('%A, %B %d')}."]

        cal = data['calendar']
        if cal['available'] and cal['count'] > 0:
            lines.append(f"📅 You have {cal['count']} event(s) today.")

        weather = data['weather']
        if weather['available']:
            lines.append(f"{weather['icon']} {weather.get('city', 'Local')}: {weather['temp']}°C, {weather['description']}")

        news = data.get('news', {})
        if news.get('available') and news.get('headlines'):
            lines.append("\n📰 Headlines:")
            for h in news['headlines'][:3]:
                lines.append(f"  • {h['title']}")

        memories = data['memories']
        if memories['available'] and memories['total_count'] > 0:
            lines.append(f"📸 {memories['total_count']} photo memories from this day!")

        shopping = data['shopping']
        if shopping['available'] and shopping['active_count'] > 0:
            lines.append(f"🛒 {shopping['active_count']} items on the shopping list")

        lines.append("\nHave a great day! 💪")
        return "\n".join(lines)

    async def deliver(self, room_id: Optional[str] = None) -> bool:
        """
        Generate and deliver the morning briefing.

        Args:
            room_id: Target room (defaults to PRIMARY_ROOM_ID)

        Returns:
            True if delivered successfully
        """
        target_room = room_id or Config.PRIMARY_ROOM_ID

        if not target_room:
            logger.warning("No target room configured for morning briefing")
            return False

        logger.info(f"Generating morning briefing for room {target_room}")

        try:
            # Gather all data
            data = await self.gather_all()

            # Generate briefing
            briefing = await self.generate_briefing(data)

            # Deliver to room
            await self.bot.send_text(target_room, f"🌅 **Morning Briefing**\n\n{briefing}")

            logger.info("Morning briefing delivered successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to deliver morning briefing: {e}")
            return False

    async def run(self) -> None:
        """
        Entry point for scheduled execution.
        Called by APScheduler at the configured time.
        """
        logger.info("Morning briefing triggered")
        await self.deliver()

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Matrix Configuration
    MATRIX_HOMESERVER_URL = os.getenv("MATRIX_HOMESERVER_URL", "http://synapse:8008")
    MATRIX_BOT_USERNAME = os.getenv("MATRIX_BOT_USERNAME", "@memu_bot:memu.local")
    MATRIX_BOT_TOKEN = os.getenv("MATRIX_BOT_TOKEN", "")

    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "database")
    DB_NAME = os.getenv("DB_NAME", "immich")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    # AI Configuration
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    # Ministral-3B recommended by community for better quality at similar resource cost
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ministral:3b")
    AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
    AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "120"))

    # Calendar Configuration (Baikal CalDAV)
    CALDAV_URL = os.getenv("CALDAV_URL", "http://calendar/dav.php")
    CALDAV_USERNAME = os.getenv("CALDAV_USERNAME", "memu")
    CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD", "")
    TIMEZONE = os.getenv("TIMEZONE", "Europe/London")

    # Morning Briefing Configuration
    BRIEFING_ENABLED = os.getenv("BRIEFING_ENABLED", "true").lower() == "true"
    BRIEFING_TIME = os.getenv("BRIEFING_TIME", "07:00")  # 24-hour format
    PRIMARY_ROOM_ID = os.getenv("PRIMARY_ROOM_ID", "")  # Matrix room for briefings

    # Weather API (OpenWeatherMap - free tier)
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    WEATHER_CITY = os.getenv("WEATHER_CITY", "London")
    WEATHER_COUNTRY = os.getenv("WEATHER_COUNTRY", "UK")

    # Immich API (for "On This Day" photos)
    IMMICH_API_URL = os.getenv("IMMICH_API_URL", "http://immich_server:2283")
    IMMICH_API_KEY = os.getenv("IMMICH_API_KEY", "")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

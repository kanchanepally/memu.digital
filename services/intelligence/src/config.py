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
    AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "30"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

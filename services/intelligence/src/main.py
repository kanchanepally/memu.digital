#!/usr/bin/env python3
"""
Memu Intelligence Service
Main entry point for the AI bot
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path if running from project root
sys.path.insert(0, str(Path(__file__).parent))

from bot import MemuBot
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def validate_config():
    """Check required config before starting"""
    required_vars = {
        'MATRIX_HOMESERVER_URL': Config.MATRIX_HOMESERVER_URL,
        'MATRIX_BOT_TOKEN': Config.MATRIX_BOT_TOKEN,
        'DB_HOST': Config.DB_HOST,
        'DB_PASSWORD': Config.DB_PASSWORD,
    }
    
    missing = [k for k, v in required_vars.items() if not v]
    
    if missing:
        logger.error(f"Missing required config: {', '.join(missing)}")
        logger.error("Check your .env file")
        return False
    
    return True

async def main():
    """Start the bot"""
    logger.info("=== Memu Intelligence Service Starting ===")
    logger.info(f"Homeserver: {Config.MATRIX_HOMESERVER_URL}")
    logger.info(f"Bot User: {Config.MATRIX_BOT_USERNAME}")
    logger.info(f"AI Enabled: {Config.AI_ENABLED}")
    logger.info(f"Ollama Host: {Config.OLLAMA_HOST}")
    
    if not validate_config():
        sys.exit(1)
    
    bot = MemuBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("=== Memu Intelligence Service Stopped ===")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Handled in main()
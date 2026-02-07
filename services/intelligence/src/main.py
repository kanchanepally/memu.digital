#!/usr/bin/env python3
"""
Memu Intelligence Service
Main entry point for the AI bot and scheduled agents
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path if running from project root
sys.path.insert(0, str(Path(__file__).parent))

from bot import MemuBot
from config import Config
from agents.briefing import MorningBriefingAgent

# APScheduler for scheduled tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

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


def setup_scheduler(bot: MemuBot) -> AsyncIOScheduler:
    """
    Set up the APScheduler with scheduled tasks.

    Currently includes:
    - Morning Briefing (default: 7:00 AM)
    """
    scheduler = AsyncIOScheduler(timezone=Config.TIMEZONE)

    # Morning Briefing
    if Config.BRIEFING_ENABLED:
        briefing_agent = MorningBriefingAgent(bot)

        # Parse briefing time (format: "HH:MM")
        try:
            hour, minute = Config.BRIEFING_TIME.split(':')
            hour, minute = int(hour), int(minute)
        except ValueError:
            logger.warning(f"Invalid BRIEFING_TIME '{Config.BRIEFING_TIME}', using default 07:00")
            hour, minute = 7, 0

        # Schedule the morning briefing
        scheduler.add_job(
            briefing_agent.run,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='morning_briefing',
            name='Morning Briefing',
            replace_existing=True
        )

        logger.info(f"Morning briefing scheduled for {hour:02d}:{minute:02d}")

        if not Config.PRIMARY_ROOM_ID:
            logger.warning(
                "PRIMARY_ROOM_ID not set. Morning briefing won't be delivered. "
                "Set this to your family room ID in .env"
            )
    else:
        logger.info("Morning briefing is disabled (BRIEFING_ENABLED=false)")

    return scheduler


async def main():
    """Start the bot and scheduler"""
    logger.info("=== Memu Intelligence Service Starting ===")
    logger.info(f"Homeserver: {Config.MATRIX_HOMESERVER_URL}")
    logger.info(f"Bot User: {Config.MATRIX_BOT_USERNAME}")
    logger.info(f"AI Enabled: {Config.AI_ENABLED}")
    logger.info(f"Ollama Host: {Config.OLLAMA_HOST}")
    logger.info(f"Timezone: {Config.TIMEZONE}")

    if not validate_config():
        sys.exit(1)

    # Create bot instance
    bot = MemuBot()

    # Set up scheduler with scheduled agents
    scheduler = setup_scheduler(bot)

    try:
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started")

        # Start the bot (this blocks until shutdown)
        await bot.start()

    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Clean shutdown
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        logger.info("=== Memu Intelligence Service Stopped ===")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Handled in main()

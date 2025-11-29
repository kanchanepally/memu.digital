import asyncio
import logging
from bot import MemuBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    bot = MemuBot()
    asyncio.run(bot.start())

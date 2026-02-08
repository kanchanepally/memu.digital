import asyncio
import logging
from memory import MemoryStore

async def main():
    print("🧹 Cleaning up Shopping List...")
    m = MemoryStore()
    await m.connect()
    
    # Execute raw SQL to clear the table
    try:
        async with m.pool.acquire() as conn:
            await conn.execute("DELETE FROM shared_lists")
        print("✅ Shopping list cleared.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await m.close()

if __name__ == "__main__":
    asyncio.run(main())

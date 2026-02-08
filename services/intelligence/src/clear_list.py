import asyncio
import logging
from memory import MemoryStore

async def main():
    print("🧹 Cleaning up Shopping List...")
    m = MemoryStore()
    await m.connect()
    
    # Execute raw SQL to clear the table
    # We can't use memory methods directly as we want a full wipe
    try:
        await m.db.execute("DELETE FROM shopping_list")
        await m.db.commit()
        print("✅ Shopping list cleared.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await m.close()

if __name__ == "__main__":
    asyncio.run(main())

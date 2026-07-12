import asyncio
import asyncpg

async def cleanup():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5433/flyrank")
    print("Clearing all data from the jobs table...")
    await conn.execute("TRUNCATE TABLE jobs;")
    print("Cleanup successful!")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(cleanup())

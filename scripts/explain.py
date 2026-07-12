import asyncio
import asyncpg

async def run_explain():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5433/flyrank")
    
    # 1. Explain Analyze Before Index
    print("=== EXPLAIN ANALYZE BEFORE INDEX ===")
    rows_before = await conn.fetch(
        "EXPLAIN ANALYZE SELECT * FROM jobs WHERE company = 'Flyrank AI';"
    )
    for row in rows_before:
        print(row[0])
        
    # 2. Create Index
    print("\nCreating index idx_jobs_company...")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);")
    
    # 3. Explain Analyze After Index
    print("\n=== EXPLAIN ANALYZE AFTER INDEX ===")
    rows_after = await conn.fetch(
        "EXPLAIN ANALYZE SELECT * FROM jobs WHERE company = 'Flyrank AI';"
    )
    for row in rows_after:
        print(row[0])
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run_explain())

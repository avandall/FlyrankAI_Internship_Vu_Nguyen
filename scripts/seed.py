import asyncio
import asyncpg
import random

companies = [
    "Flyrank AI", "Google", "Meta", "Amazon", "Netflix", "Microsoft", "Apple", "OpenAI", "Anthropic", "Stripe"
]
titles = [
    "Software Engineer", "AI Researcher", "Data Scientist", "Product Manager", "Backend Engineer", 
    "Frontend Developer", "DevOps Engineer", "Machine Learning Engineer"
]

async def seed():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5433/flyrank")
    
    print("Clearing existing jobs...")
    await conn.execute("TRUNCATE TABLE jobs;")
    
    print("Generating 10,000 jobs...")
    jobs = []
    for i in range(10000):
        job_id = f"job-{i}"
        title = random.choice(titles)
        company = random.choice(companies)
        description = f"This is job description number {i}."
        jobs.append((job_id, title, company, description))
        
    print("Inserting jobs...")
    await conn.executemany(
        """
        INSERT INTO jobs (id, title, company, description)
        VALUES ($1, $2, $3, $4)
        """,
        jobs
    )
    print("Successfully seeded 10,000 rows!")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())

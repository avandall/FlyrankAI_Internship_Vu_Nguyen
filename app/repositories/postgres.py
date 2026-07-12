import asyncpg
from app.domain.entities import Job
from app.domain.interfaces import JobRepository

class PostgresJobRepository(JobRepository):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, job: Job) -> Job:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO jobs (id, title, company, description, created_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE
                SET title = EXCLUDED.title,
                    company = EXCLUDED.company,
                    description = EXCLUDED.description,
                    created_at = EXCLUDED.created_at
                """,
                job.id,
                job.title,
                job.company,
                job.description,
                job.created_at,
            )
        return job

    async def get_by_id(self, job_id: str) -> Job | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, title, company, description, created_at FROM jobs WHERE id = $1",
                job_id,
            )
            if not row:
                return None
            return Job(
                id=row["id"],
                title=row["title"],
                company=row["company"],
                description=row["description"],
                created_at=row["created_at"],
            )

    async def list_all(self) -> list[Job]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, title, company, description, created_at FROM jobs ORDER BY created_at DESC"
            )
            return [
                Job(
                    id=row["id"],
                    title=row["title"],
                    company=row["company"],
                    description=row["description"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

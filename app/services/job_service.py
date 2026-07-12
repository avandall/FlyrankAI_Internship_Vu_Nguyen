from app.domain.entities import Job
from app.domain.interfaces import JobRepository

class JobService:
    def __init__(self, repository: JobRepository):
        self.repository = repository

    async def create_job(self, job: Job) -> Job:
        # Business rules or validation can go here
        return await self.repository.save(job)

    async def get_job(self, job_id: str) -> Job | None:
        return await self.repository.get_by_id(job_id)

    async def list_jobs(self) -> list[Job]:
        return await self.repository.list_all()

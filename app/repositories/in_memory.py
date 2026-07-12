from app.domain.entities import Job
from app.domain.interfaces import JobRepository

class InMemoryJobRepository(JobRepository):
    def __init__(self):
        self._jobs: dict[str, Job] = {}

    async def save(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job

    async def get_by_id(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    async def list_all(self) -> list[Job]:
        return list(self._jobs.values())

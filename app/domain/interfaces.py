from abc import ABC, abstractmethod
from app.domain.entities import Job

class JobRepository(ABC):
    @abstractmethod
    async def save(self, job: Job) -> Job:
        """Persist a Job entity to storage."""
        pass

    @abstractmethod
    async def get_by_id(self, job_id: str) -> Job | None:
        """Retrieve a Job entity by its unique ID."""
        pass

    @abstractmethod
    async def list_all(self) -> list[Job]:
        """Retrieve all Job entities from storage."""
        pass

from datetime import datetime, timezone
from pydantic import BaseModel, Field

class Job(BaseModel):
    id: str
    title: str
    company: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Task(BaseModel):
    id: int | None = None
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    title: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None




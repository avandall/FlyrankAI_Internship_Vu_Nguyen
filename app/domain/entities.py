from datetime import datetime, timezone
from pydantic import BaseModel, Field

class Job(BaseModel):
    id: str
    title: str
    company: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

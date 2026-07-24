from fastapi import APIRouter
from app.domain.entities import Task
from app.repositories.sqlite_task import SQLiteTaskRepository

router = APIRouter(prefix="/tasks", tags=["Tasks"])
task_repository = SQLiteTaskRepository()

@router.get("", response_model=list[Task])
@router.get("/", response_model=list[Task])
def get_tasks():
    return task_repository.list_all()

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.domain.entities import Task
from app.repositories.sqlite_task import SQLiteTaskRepository

router = APIRouter(prefix="/tasks", tags=["Tasks"])
task_repository = SQLiteTaskRepository()

@router.get("", response_model=list[Task])
@router.get("/", response_model=list[Task])
def get_tasks():
    return task_repository.list_all()

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = task_repository.find_by_id(task_id)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return task
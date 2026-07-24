from fastapi import APIRouter, status, Response
from fastapi.responses import JSONResponse
from app.domain.entities import Task, TaskCreate, TaskUpdate
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

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Task)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(payload: TaskCreate):
    if not payload.title or not payload.title.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required"}
        )
    return task_repository.create(payload.title.strip())

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None or not payload.title.strip() or payload.done is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title and done status are required"}
        )
    
    updated_task = task_repository.update(task_id, payload.title.strip(), payload.done)
    if not updated_task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    deleted = task_repository.delete(task_id)
    if not deleted:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"}
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
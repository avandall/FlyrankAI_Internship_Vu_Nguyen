from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, Response
from database import init_db, get_db
from models import Task, TaskCreate, TaskUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="AI Generated Tasks API", lifespan=lifespan)

@app.get("/tasks", response_model=list[Task])
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [Task(id=row["id"], title=row["title"], done=bool(row["done"])) for row in rows]

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return Task(id=row["id"], title=row["title"], done=bool(row["done"]))

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate):
    if not payload.title or not payload.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required"})
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (payload.title.strip(), 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return Task(id=new_id, title=payload.title.strip(), done=False)

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    if not payload.title or not payload.title.strip() or payload.done is None:
        return JSONResponse(status_code=400, content={"error": "Title and done status are required"})
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (payload.title.strip(), 1 if payload.done else 0, task_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected == 0:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return Task(id=task_id, title=payload.title.strip(), done=payload.done)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected == 0:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return Response(status_code=204)

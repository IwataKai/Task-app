from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Task App", version="0.1.0")


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class Task(TaskCreate):
    id: str
    completed: bool = False
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None


TASKS: Dict[str, Task] = {}


@app.get("/health")

def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=List[Task])

def list_tasks() -> List[Task]:
    return list(TASKS.values())


@app.post("/tasks", response_model=Task, status_code=201)

def create_task(payload: TaskCreate) -> Task:
    now = datetime.utcnow()
    task = Task(id=str(uuid4()), created_at=now, updated_at=now, **payload.dict())
    TASKS[task.id] = task
    return task


@app.get("/tasks/{task_id}", response_model=Task)

def get_task(task_id: str) -> Task:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)

def update_task(task_id: str, payload: TaskUpdate) -> Task:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = payload.dict(exclude_unset=True)
    updated_task = task.copy(update=update_data)
    updated_task.updated_at = datetime.utcnow()
    TASKS[task_id] = updated_task
    return updated_task


@app.delete("/tasks/{task_id}", status_code=204)

def delete_task(task_id: str) -> None:
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    del TASKS[task_id]

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.models import Task
from app.modules.tasks.schemas import CreateTaskSchema, UpdateTaskSchema


class TasksService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_all(self) -> list[Task]:
        result = await self.db.execute(select(Task).order_by(Task.created_at.desc()))
        return list(result.scalars().all())

    async def find_one(self, task_id: str) -> Task:
        task = await self.db.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    async def create(self, data: CreateTaskSchema) -> Task:
        task = Task(**data.model_dump())
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task_id: str, data: UpdateTaskSchema) -> Task:
        task = await self.find_one(task_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: str) -> None:
        task = await self.find_one(task_id)
        await self.db.delete(task)
        await self.db.commit()

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.schemas import CreateTaskSchema, TaskResponse, UpdateTaskSchema
from app.modules.tasks.service import TasksService
from app.shared.database.engine import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_service(db: AsyncSession = Depends(get_db)) -> TasksService:
    return TasksService(db)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(service: TasksService = Depends(_get_service)) -> list[TaskResponse]:
    tasks = await service.find_all()
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, service: TasksService = Depends(_get_service)) -> TaskResponse:
    task = await service.find_one(task_id)
    return TaskResponse.model_validate(task)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: CreateTaskSchema, service: TasksService = Depends(_get_service)) -> TaskResponse:
    task = await service.create(data)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str, data: UpdateTaskSchema, service: TasksService = Depends(_get_service)
) -> TaskResponse:
    task = await service.update(task_id, data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, service: TasksService = Depends(_get_service)) -> None:
    await service.delete(task_id)

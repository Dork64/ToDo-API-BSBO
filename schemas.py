from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название задачи"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание задачи"
    )
    is_important: bool = Field(
        ...,
        description="Важность задачи"
    )
    deadline_at: datetime = Field(
        ...,
        description="Плановый дедлайн задачи (дата и время)"
    )


class TaskCreate(TaskBase):
    """
    Создание задачи:
    - title
    - description (опц.)
    - is_important
    - deadline_at
    """
    pass


class TaskUpdate(BaseModel):
    """
    Частичное обновление задачи.
    is_urgent тут нет — оно считается автоматически.
    """
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Новое название задачи"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Новое описание"
    )
    is_important: Optional[bool] = Field(
        None,
        description="Новая важность"
    )
    completed: Optional[bool] = Field(
        None,
        description="Статус выполнения"
    )
    deadline_at: Optional[datetime] = Field(
        None,
        description="Новый дедлайн задачи"
    )


class TaskResponse(TaskBase):
    id: int = Field(
        ...,
        description="Уникальный идентификатор задачи",
        examples=[1]
    )
    quadrant: str = Field(
        ...,
        description="Квадрант матрицы Эйзенхауэра (Q1, Q2, Q3, Q4)",
        examples=["Q1"]
    )
    is_urgent: bool = Field(
        ...,
        description="Срочность задачи (рассчитана автоматически)"
    )
    completed: bool = Field(
        default=False,
        description="Статус выполнения задачи"
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания задачи"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Дата и время завершения задачи"
    )
    days_left: Optional[int] = Field(
        None,
        description="Оставшийся срок до дедлайна в днях (расчётное поле)"
    )

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from typing import List
from datetime import datetime, timezone

from database import get_async_session
from models import Task, User
from schemas import TimingStatsResponse, TaskResponse
from utils import calculate_days_until_deadline
from routers.auth import get_current_user  
router = APIRouter(
    prefix="/stats",
    tags=["statistics"]
)


@router.get("/", response_model=dict)
async def get_tasks_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> dict:


    # Базовое условие фильтрации по пользователю
    user_filter = []
    if current_user.role.value != "admin":
        user_filter = [Task.user_id == current_user.id]

    # Общее количество задач
    total_result = await db.execute(
        select(func.count(Task.id)).where(*user_filter)
    )
    total_tasks = total_result.scalar() or 0

    # Подсчет по квадрантам (одним запросом)
    quadrant_result = await db.execute(
        select(
            Task.quadrant,
            func.count(Task.id).label("count")
        )
        .where(*user_filter)
        .group_by(Task.quadrant)
    )

    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for row in quadrant_result:
        if row.quadrant in by_quadrant:
            by_quadrant[row.quadrant] = row.count

    # Подсчет по статусу (одним запросом)
    status_result = await db.execute(
        select(
            func.count(case((Task.completed == True, 1))).label("completed"),
            func.count(case((Task.completed == False, 1))).label("pending"),
        ).where(*user_filter)
    )

    status_row = status_result.one()
    by_status = {
        "completed": status_row.completed or 0,
        "pending": status_row.pending or 0,
    }

    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status,
    }


@router.get("/timing", response_model=TimingStatsResponse)
async def get_deadline_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> TimingStatsResponse:


    now_utc = datetime.now(timezone.utc)

    statement = select(
        func.sum(
            case(
                (
                    (Task.completed == True)
                    & (Task.completed_at <= Task.deadline_at),
                    1,
                ),
                else_=0,
            )
        ).label("completed_on_time"),
        func.sum(
            case(
                (
                    (Task.completed == True)
                    & (Task.completed_at > Task.deadline_at),
                    1,
                ),
                else_=0,
            )
        ).label("completed_late"),
        func.sum(
            case(
                (
                    (Task.completed == False)
                    & (Task.deadline_at != None)
                    & (Task.deadline_at > now_utc),
                    1,
                ),
                else_=0,
            )
        ).label("on_plan_pending"),
        func.sum(
            case(
                (
                    (Task.completed == False)
                    & (Task.deadline_at != None)
                    & (Task.deadline_at <= now_utc),
                    1,
                ),
                else_=0,
            )
        ).label("overdue_pending"),
    ).select_from(Task)

    # Фильтр по пользователю, если не админ
    if current_user.role.value != "admin":
        statement = statement.where(Task.user_id == current_user.id)

    result = await db.execute(statement)
    stats_row = result.one()

    return TimingStatsResponse(
        completed_on_time=stats_row.completed_on_time or 0,
        completed_late=stats_row.completed_late or 0,
        on_plan_pending=stats_row.on_plan_pending or 0,
        overtime_pending=stats_row.overdue_pending or 0,
    )


@router.get("/today", response_model=List[TaskResponse])
async def get_today_deadline_tasks(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> List[TaskResponse]:
    """
    Задачи, дедлайн по которым наступает СЕГОДНЯ.
    Админ видит все, пользователь — только свои невыполненные задачи.
    """

    today_utc = datetime.now(timezone.utc).date()

    base_query = select(Task).where(
        Task.completed == False,
        Task.deadline_at.is_not(None),
        func.date(Task.deadline_at) == today_utc,
    )

    # Фильтр по пользователю
    if current_user.role.value != "admin":
        base_query = base_query.where(Task.user_id == current_user.id)

    result = await db.execute(base_query)
    tasks = result.scalars().all()

    response: List[TaskResponse] = []

    for task in tasks:
        days_deadline = calculate_days_until_deadline(task.deadline_at)

        task_dict = task.to_dict()
        task_dict["days_until_deadline"] = days_deadline

        if (
            task.deadline_at is not None
            and days_deadline is not None
            and days_deadline < 0
        ):
            task_dict["status_message"] = "Задача просрочена"
        else:
            task_dict["status_message"] = "Время поднапрячься!"

        response.append(TaskResponse(**task_dict))

    return response

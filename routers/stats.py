from fastapi import APIRouter
from database import tasks_db

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    responses={404: {"description": "Not found"}}
)

@router.get("")
async def get_tasks_stats() -> dict:
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    completed_count = 0
    pending_count = 0

    for task in tasks_db:
        q = task.get("quadrant")
        if q in by_quadrant:
            by_quadrant[q] += 1

        if task.get("completed"):
            completed_count += 1
        else:
            pending_count += 1

    return {
        "total_tasks": len(tasks_db),
        "by_quadrant": by_quadrant,
        "by_status": {
            "completed": completed_count,
            "pending": pending_count
        }
    }

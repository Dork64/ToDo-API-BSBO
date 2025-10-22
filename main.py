# Главный файл приложения
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime



app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact = {"name": "Вьюгин Иван Андреевич"}
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]



@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "contact": app.contact
    }

@app.get("/tasks") 
async def get_all_tasks() -> dict: 
    return { 
        "count": len(tasks_db),  # считает количество записей в хранилище 
        "tasks": tasks_db # выводит всё, чта есть в хранилище 
    } 
 
@app.get("/tasks/quadrant/{quadrant}") 
async def get_tasks_by_quadrant(quadrant: str) -> dict: 
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]: 
        raise HTTPException(    #специальный класс в FastAPI для возврата HTTP ошибок. Не забудьте добавть его вызов в 1 строке 
            status_code=400, 
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"  #текст, который будет выведен пользователю   
        ) 
    
    filtered_tasks = [ 
        task                          # ЧТО добавляем в список 
        for task in tasks_db          # ОТКУДА берем элементы 
        if task["quadrant"] == quadrant  # УСЛОВИЕ фильтрации 
    ] 
    
    return { 
        "quadrant": quadrant, 
        "count": len(filtered_tasks), 
        "tasks": filtered_tasks 
}

@app.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    completed_count = 0
    pending_count = 0

    # Проход по всем задачам и подсчёт статистики
    for task in tasks_db:
        quadrant = task["quadrant"]
        if quadrant in by_quadrant:
            by_quadrant[quadrant] += 1
        
        # Увеличиваем счётчик по статусу
        if task["completed"]:
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

@app.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException( 
            status_code=400,
            detail="Статус не найден"
        )

    filtered_tasks = [
        task for task in tasks_db
        if (status == "completed" and task["completed"]) or
           (status == "pending" and not task["completed"])
    ]
    
    # Если задач нет, возвращаем пустой список (не 404)
    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@app.get("/tasks/search")
async def search_tasks(q: str = Query(..., min_length=2)) -> dict:

    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Ключевое слово должно содержать минимум 2 символа"
        )

    search_term = q.lower()

    filtered_tasks = [
        task for task in tasks_db
        if (
            search_term in task["title"].lower() or
            (task["description"] is not None and search_term in str(task["description"]).lower())
        )
    ]

    # Если задач не найдено — возвращаем 404
    if not filtered_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи, содержащие '{q}', не найдены"
        )

    return {
        "query": q,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    # Ищем задачу по ID
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Задача с ID {task_id} не найдена"
        )
    
    return task


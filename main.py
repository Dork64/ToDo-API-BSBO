# Главный файл приложения
from fastapi import FastAPI
from routers import tasks, stats 




app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact = {"name": "Вьюгин Иван Андреевич"}
)

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1") 

@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "contact": app.contact
    }

@app.post("/tasks")
async def create_task(task: dict):
    return {"message": "Запись успешно создана!", "task": task}


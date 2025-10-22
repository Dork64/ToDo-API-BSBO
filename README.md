# ToDo лист API

## Описание
API для управления задачами с использованием матрицы Эйзенхауэра.

## Технологии
- FastAPI
- Python 3.x
- Временное хранилище в памяти

## Доступные эндпоинты
- `GET /` — метаданные API
- `GET /tasks` — все задачи
- `GET /tasks/quadrant/{quadrant}` — по квадранту (Q1–Q4)
- `GET /tasks/stats` — статистика
- `GET /tasks/status/{status}` — по статусу (completed/pending)
- `GET /tasks/search?q={query}` — поиск по ключевому слову (≥2 символа)
- `GET /tasks/{task_id}` — по ID задачи

## Запуск
1. Установите зависимости:  
   pip install fastapi uvicorn
2. Запустите сервер:  
   uvicorn main:app --reload
3. Откройте в браузере: `http://127.0.0.1:8000`

## Автор
Вьюгин Иван Андреевич
# ToDo лист API

## Описание
API для управления задачами с использованием матрицы Эйзенхауэра. Текущая версия использует PostgreSQL (Supabase) и асинхронный доступ к базе данных через SQLAlchemy 2.0 и asyncpg.

## Технологии
- FastAPI
- Python 3.x
- PostgreSQL (Supabase)
- SQLAlchemy (async)
- asyncpg
- Pydantic v2
- Uvicorn

## Доступные эндпоинты
- `GET /` — метаданные API
- `GET /health` — проверка статуса API и подключения к БД

### Эндпоинты задач (`/api/v2/tasks`)
- `GET /api/v2/tasks` — все задачи
- `GET /api/v2/tasks/quadrant/{quadrant}` — по квадранту (Q1–Q4)
- `GET /api/v2/tasks/status/{status}` — по статусу (completed/pending)
- `GET /api/v2/tasks/search?q={query}` — поиск по ключевому слову (≥2 символа)
- `GET /api/v2/tasks/{task_id}` — по ID задачи
- `POST /api/v2/tasks` — создание задачи
- `PUT /api/v2/tasks/{task_id}` — обновление задачи
- `PATCH /api/v2/tasks/{task_id}/complete` — отметить выполненной
- `DELETE /api/v2/tasks/{task_id}` — удаление задачи

### Эндпоинты статистики (`/api/v2/stats`)
- `GET /api/v2/stats` — общая статистика:
  - количество задач
  - распределение по квадрантам
  - количество выполненных и невыполненных задач

## Подготовка окружения
1. Создайте файл `.env`:
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

2. Установите зависимости:
pip install -r requirements.txt

3. Пример `requirements.txt`:
fastapi==0.119.0
pydantic==2.12.0
unicorn==2.1.4
uvicorn==0.37.0
SQLAlchemy==2.0.36
asyncpg==0.29.0
python-dotenv==1.0.1
typing-extensions==4.12.2

## Запуск
1. Активируйте виртуальное окружение.
2. Запустите сервер:
uvicorn main:app --reload
3. Откройте в браузере:
- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Автор
Вьюгин Иван Андреевич
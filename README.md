# ToDo лист API

## Описание
API для управления задачами по матрице Эйзенхауэра. Текущая версия использует PostgreSQL (Supabase) и асинхронный доступ к базе данных через SQLAlchemy 2.0 и asyncpg. Добавлена поддержка планового дедлайна: срочность (`is_urgent`) теперь рассчитывается автоматически на основе разницы между текущей датой и дедлайном, а квадрант определяется по важности и вычисленной срочности. Планировщик (APScheduler) периодически пересчитывает срочность и квадранты всех невыполненных задач, поддерживая актуальность данных даже без пользовательских запросов.

## Технологии
- FastAPI  
- Python 3.x  
- PostgreSQL (Supabase)  
- SQLAlchemy 2.x (async)  
- asyncpg  
- Pydantic v2  
- Uvicorn
- APScheduler  

## Эндпоинты

### Общие
- `GET /` — метаданные API  
- `GET /health` — проверка работоспособности API и соединения с БД  

### Эндпоинты задач (`/api/v2/tasks`)
- `GET /api/v2/tasks` — получить все задачи  
- `GET /api/v2/tasks/quadrant/{quadrant}` — получить задачи по квадранту (Q1–Q4)  
- `GET /api/v2/tasks/status/{status}` — получить задачи по статусу (`completed` / `pending`)  
- `GET /api/v2/tasks/search?q={query}` — поиск задач (минимум 2 символа)  
- `GET /api/v2/tasks/{task_id}` — получить задачу по ID  
- `POST /api/v2/tasks` — создать задачу (срочность высчитывается автоматически)  
- `PUT /api/v2/tasks/{task_id}` — обновить задачу (пересчёт срочности и квадранта)  
- `PATCH /api/v2/tasks/{task_id}/complete` — отметить задачу выполненной  
- `DELETE /api/v2/tasks/{task_id}` — удалить задачу  

### Эндпоинты статистики (`/api/v2/stats`)
- `GET /api/v2/stats` — общая статистика:
  - количество задач  
  - распределение по квадрантам  
  - выполненные / невыполненные  

- `GET /api/v2/stats/deadlines` — статистика по невыполненным задачам:
  - название  
  - описание  
  - дата создания  
  - дедлайн  
  - оставшиеся дни до дедлайна 
  
- `GET /api/v2/stats/timing` — статистика по срокам выполнения:
  - completed_on_time — задачи, завершённые в срок 
  - completed_late — задачи, завершённые с опозданием 
  - дата создания  
  - on_plan_pending — невыполненные задачи, у которых дедлайн ещё не наступил  
  - overtime_pending — невыполненные задачи с просроченным дедлайном 

  - `GET /api/v2/stats/today` — задачи со сроком выполнения сегодня:

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
APScheduler==3.10.4

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

 Инструкция по запуску

Клонируем репозиторий:

```bash
git clone https://github.com/G0shan4ik/cinema_univer
```


## Вариант 1. Через Docker Compose

Из корня проекта ./cinema_univer выполнить:

```bash
docker compose up --build
```

После запуска сервисы будут доступны по адресам:

- фронтенд: `http://localhost:8080`
- бэкенд: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Вариант 2. Локальный запуск без Docker

### 1. Запустить PostgreSQL

Нужна локальная база PostgreSQL с параметрами:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cinema
DEBUG=True
```

Эти значения уже указаны в [need.env](C:/Users/egork/Documents/New%20project/cinema2_0/need.env).

### 2. Запустить backend

Перейти в папку [cinema2_0](C:/Users/egork/Documents/New%20project/cinema2_0) и выполнить:

```bash
pip install poetry
poetry install
poetry run dev
```

Backend поднимется на `http://127.0.0.1:8000`.

### 3. Запустить frontend

Перейти в папку [frontend](C:/Users/egork/Documents/New%20project/frontend) и выполнить:

```bash
npm install
npm run serve
```

Frontend поднимется на `http://localhost:8080`.

# Cinema 2.0 Backend

Бэкенд для лабораторной работы по сайту кинотеатра на `FastAPI + SQLAlchemy + PostgreSQL`.

## Что реализовано

- регистрация, вход и восстановление пользователя
- фильмы, залы и сеансы
- бронирование билетов и смена статуса билета
- получение занятых мест на сеанс
- избранные фильмы пользователя

## Структура

- `backend/database/models.py` — модели БД
- `backend/database/methods/` — слой работы с таблицами
- `backend/api/datamodels.py` — pydantic-модели
- `backend/api/routers/` — API роутеры
- `main.py` — точка входа

## Запуск

1. Заполнить `.env` по примеру из `need.env`
2. Установить зависимости
3. Запустить:

```bash
poetry run dev
```

## Docker

Для запуска из корня проекта через `docker compose` используется отдельный контейнер `postgres`, к которому backend подключается автоматически.

## Демо-пользователи

- `admin@cinemahub.com` / `admin123`
- `user@cinemahub.com` / `user123`

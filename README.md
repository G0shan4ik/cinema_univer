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

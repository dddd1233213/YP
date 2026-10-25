# Team Finder

Поиск команды для pet-проектов (Django MVT, вариант «Избранное»).

## Запуск (основной путь — Docker Compose)

```bash
cp .env.example .env   # при желании поменять секреты/пароли
docker compose up --build
```

Откройте http://127.0.0.1:8000/.

Compose поднимает два сервиса: `web` (Django) и `db` (Postgres 16).
Данные лежат в named volumes (`postgres-data`, `media`).

## Локальная разработка (без Docker)

Нужен локальный PostgreSQL 16.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
export POSTGRES_HOST=localhost POSTGRES_USER=teamfinder \
  POSTGRES_PASSWORD=teamfinder POSTGRES_DB=teamfinder
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

## Проверки

```bash
.venv/bin/python manage.py check
.venv/bin/flake8 .
.venv/bin/python manage.py test
```

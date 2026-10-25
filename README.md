# Team Finder

Поиск команды для pet-проектов: пользователи публикуют проекты, присоединяются
к чужим, отмечают избранное. Django MVT-монолит, вариант «Избранное».

## Быстрый старт (Docker — основной путь)

Нужен только Docker. Без `.env` тоже работает — в compose зашиты dev-дефолты.

```bash
docker compose up --build
```

Открыть http://127.0.0.1:8000/. Остановка с удалением данных:

```bash
docker compose down -v
```

При старте entrypoint автоматически: `migrate` → создание суперпользователя
(если нет) → `seed_demo` (если БД пустая) → gunicorn на `:8000`.

Свои секреты — через `.env` (все ключи см. в `.env.example`):

```bash
cp .env.example .env   # поменять пароли при желании
docker compose up --build
```

## Демо-учётки

Пароль всех демо-пользователей: значение `SEED_PASSWORD` (дефолт `demo12345`).

| Email | Имя | Роль в сиде |
|---|---|---|
| anna@example.com | Анна Соколова | автор «Веб-приложение для команды» + «Архивный проект Анны», участник проекта Бориса |
| boris@example.com | Борис Волков | автор «Мобильное приложение», участник проекта Анны |
| vera@example.com | Вера Орлова | автор «Дизайн-система», участник проекта Анны |
| admin@example.com | Admin Root | суперпользователь (из `DJANGO_SUPERUSER_*`, дефолт-пароль `admin12345`) |

## Что где

- `/` — главная, список проектов (новые сверху, пагинация 12).
- `/projects/<pk>/` — детальная проекта: присоединение, завершение
  (владелец), иконка избранного, кнопка «Поделиться ссылкой на проект»
  (копирует URL в буфер, fallback — prompt).
- `/projects/create/`, `/projects/<pk>/edit/` — создание/редактирование
  (гость редиректится на login).
- `/users/list/` — список пользователей + фильтры варианта 1
  (только для авторизованных; гость видит просто список).
- `/users/<pk>/` — профиль: контакты раскрываются по кнопке, владелец видит
  «Редактировать профиль» и «Поделиться профилем».
- `/favorites/` — избранное текущего пользователя (login required).
- `/admin/` — админка: пользователи, проекты, участия, избранное.

### Фильтры `/users/list/?filter=`

| Значение | Название | Смысл |
|---|---|---|
| `favorite_authors` | Авторы избранных проектов | авторы проектов в моём избранном (без меня) |
| `my_projects_participants` | Участники моих проектов | участники проектов, где я автор |
| `fans` | Поклонники | пользователи, добавившие мои проекты в избранное (без меня) |
| `teammates` | Сокомандники | авторы проектов, где я участник |

Невалидное значение игнорируется (полный список). Активный фильтр подсвечен,
есть кнопка «Сбросить».

## Локальная разработка (без Docker)

Нужен локальный PostgreSQL 16.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
export POSTGRES_HOST=localhost POSTGRES_USER=teamfinder \
  POSTGRES_PASSWORD=teamfinder POSTGRES_DB=teamfinder
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo   # демо-данные, идемпотентно
.venv/bin/python manage.py runserver
```

Суперпользователь локально:

```bash
export DJANGO_SUPERUSER_EMAIL=admin@example.com \
  DJANGO_SUPERUSER_PASSWORD=admin12345 \
  DJANGO_SUPERUSER_FIRST_NAME=Admin DJANGO_SUPERUSER_LAST_NAME=Root
.venv/bin/python manage.py createsuperuser --noinput
```

## Структура проекта

```text
config/        # settings (единый, всё через env), urls, wsgi
users/         # кастомный User (email-логин), auth views, профиль, фильтры, seed_demo
projects/      # Project/Membership, CRUD, join/finish, главная
favorites/     # Favorite, toggle + страница избранного
templates/     # base.html + шаблоны приложений
static/js/     # share.js (копирование ссылки, без зависимостей)
docker/        # entrypoint.sh (migrate → superuser → seed → gunicorn)
Dockerfile     # python:3.13-slim, collectstatic при сборке, ENTRYPOINT entrypoint.sh
docker-compose.yml  # db postgres:16 + web, healthcheck, named volumes
```

## Проверки

```bash
.venv/bin/python manage.py check
.venv/bin/flake8 .
.venv/bin/python manage.py test
```

CI (`.github/workflows/ci.yml`): flake8 + `manage.py test` на каждый push/PR,
PostgreSQL 16 сервисом.

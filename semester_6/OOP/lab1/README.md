# Лабораторна робота 1 — Система періодичних видань

Серверний MVC вебдодаток на Python без веб-фреймворків. HTTP обробляється через `http.server`, маршрутизація, MVC, Command Pattern, session-cookie та DAO реалізовані вручну.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
createdb periodicals
psql periodicals -f sql/schema.sql
psql periodicals -f sql/seed.sql
python -m app.main
```

За замовчуванням сервер доступний на `http://127.0.0.1:8000`.

Тестові користувачі: `admin/password`, `reader/password`.

## Налаштування

`DATABASE_URL` можна передати через змінну середовища, наприклад:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/periodicals
```

## Тести

```bash
python -m unittest discover -s tests
```

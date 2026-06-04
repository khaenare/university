# Лабораторна робота 1 — Система періодичних видань

Серверний вебдодаток для керування каталогом періодичних видань, оформлення передплат і реєстрації платежів.

Проєкт реалізовано на Python без високорівневих веб-фреймворків. HTTP-запити обробляються через `http.server`, routing, MVC, Command Pattern, DAO, session-cookie та авторизація реалізовані вручну.

## Тема

**Система Періодичні видання**

Адміністратор здійснює ведення каталогу періодичних видань. Читач може оформити передплату, попередньо вибравши періодичне видання зі списку. Система підраховує суму для оплати та реєструє платіж.

## Реалізовані вимоги

- Використано менеджер пакетів `pip` і файл `requirements.txt`.
- HTTP-сервер реалізовано на базі `http.server`.
- Реалізовано власний routing engine.
- Реалізовано Front Controller.
- Реалізовано MVC pattern без MVC-фреймворків.
- Реалізовано Command Pattern для обробки маршрутів.
- Реалізовано DAO pattern для доступу до БД.
- Використано PostgreSQL як SQL базу даних.
- CRUD-запити написані вручну через SQL, ORM не використовується.
- Views реалізовано через `jinja2` templates.
- Маніпуляції з даними виконуються через HTTP forms.
- Реалізовано login/password.
- Реалізовано session на основі cookie.
- Внутрішні сторінки захищені redirect-ом на `/login`.
- Додано logging HTTP-запитів, login-подій, 404 і помилок.
- Код покрито unit-тестами.
- Додано Docker Compose для швидкого запуску застосунку з PostgreSQL.

## Технології

- Python 3.13
- `http.server`
- `http.cookies`
- `psycopg`
- PostgreSQL 17
- Jinja2
- Docker Compose
- `unittest`

## Архітектура

Проєкт побудований за класичною серверною архітектурою:

```text
Incoming HTTP Request
        |
        v
FrontController на базі BaseHTTPRequestHandler
        |
        v
Custom Router
        |
        v
Command
        |
        v
Controller
        |
        v
Service
        |
        v
DAO
        |
        v
PostgreSQL
```

Відповідь формується через Jinja template:

```text
Controller -> Model data -> View template -> HTML Response
```

## Структура проєкту

```text
lab1/
  app/
    main.py
    config.py

    core/
      request.py
      response.py
      router.py
      controller.py
      session.py
      template_engine.py

    commands/
      base.py

    controllers/
      auth_controller.py
      publication_controller.py
      subscription_controller.py

    dao/
      connection.py
      user_dao.py
      publication_dao.py
      subscription_dao.py
      payment_dao.py

    models/
      user.py
      publication.py
      subscription.py
      subscription_summary.py
      payment.py

    services/
      auth_service.py
      publication_service.py
      subscription_service.py

    views/
      layout.html
      login.html
      publications.html
      publication_form.html
      subscriptions.html
      payment.html
      error.html

    static/
      style.css

  sql/
    schema.sql
    seed.sql

  tests/
    test_auth_service.py
    test_request.py
    test_router.py
    test_subscription_controller.py
    test_subscription_service.py

  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
```

## Функціонал

### Авторизація

- Сторінка входу: `/login`.
- Вхід виконується через HTML form методом `POST`.
- Після успішного входу створюється session id.
- Session id зберігається у cookie `SESSION_ID`.
- Якщо користувач без сесії відкриває внутрішню сторінку, сервер повертає redirect на `/login`.
- Вихід із системи: `/logout`.

### Ролі

У системі є дві ролі:

- `admin` — адміністратор каталогу.
- `reader` — читач, який оформлює передплати та платежі.

### Адміністратор

Адміністратор може:

- переглядати каталог видань;
- створювати нові періодичні видання;
- редагувати назву, видавця, періодичність і ціну;
- видаляти видання.

Сторінки:

- `/publications`
- `/publications/new`

### Читач

Читач може:

- переглядати каталог періодичних видань;
- оформлювати передплату на вибране видання;
- вибирати кількість місяців;
- переглядати свої передплати;
- змінювати термін передплати;
- видаляти свою передплату;
- реєструвати платіж;
- переглядати платежі конкретної передплати;
- змінювати статус платежу;
- видаляти платіж.

Сторінки:

- `/publications`
- `/subscriptions`
- `/payment`

### Розрахунок суми

Сума передплати рахується у service layer:

```text
total_amount = publication.price * months
```

DAO не містить бізнес-логіки. Він тільки виконує SQL-запити.

### Захист доступу

- Неавторизований користувач перенаправляється на `/login`.
- Читач не може створювати, редагувати або видаляти видання.
- Читач не може оплатити чужу передплату.
- Читач не може переглядати або змінювати чужі платежі.

## UI

Інтерфейс оформлено як сучасний каталог періодики:

- темна верхня панель навігації;
- окрема login-сторінка з hero-блоком;
- каталог видань у вигляді карточок;
- dashboard для передплат;
- окрема сторінка платежів;
- badges для статусів і видавців;
- адаптивна верстка для desktop і mobile;
- стилізовані форми, кнопки, таблиці та повідомлення про помилки.

## Дані в базі

Seed-дані містять:

- 5 користувачів;
- 20 періодичних видань;
- 5 передплат;
- 3 платежі.

Тестові користувачі:

| Login | Password | Role |
|---|---|---|
| `admin` | `password` | `admin` |
| `reader` | `password` | `reader` |
| `olena` | `password` | `reader` |
| `maksym` | `password` | `reader` |
| `iryna` | `password` | `reader` |

## Швидкий запуск через Docker Compose

Найпростіший спосіб запустити проєкт:

```bash
docker compose up --build
```

Після запуску застосунок буде доступний за адресою:

```text
http://127.0.0.1:8000/login
```

Docker Compose запускає:

- контейнер PostgreSQL;
- контейнер Python-застосунку;
- автоматично застосовує `sql/schema.sql`;
- автоматично застосовує `sql/seed.sql`.

Щоб запустити у background-режимі:

```bash
docker compose up --build -d
```

Щоб подивитися статус контейнерів:

```bash
docker compose ps
```

Щоб подивитися логи:

```bash
docker compose logs -f
```

Щоб зупинити контейнери:

```bash
docker compose down
```

Щоб повністю пересоздати базу з seed-даними:

```bash
docker compose down -v
docker compose up --build
```

## Локальний запуск без Docker

Потрібно мати встановлений PostgreSQL і CLI-команди `createdb`, `psql`.

Створити virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Встановити залежності:

```bash
pip install -r requirements.txt
```

Створити базу даних:

```bash
createdb periodicals
```

Застосувати schema і seed:

```bash
psql periodicals -f sql/schema.sql
psql periodicals -f sql/seed.sql
```

Запустити застосунок:

```bash
python -m app.main
```

Відкрити у браузері:

```text
http://127.0.0.1:8000/login
```

## Налаштування

За замовчуванням застосунок використовує такі параметри:

```text
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/periodicals
```

Їх можна змінити через змінні середовища:

```bash
export APP_HOST=127.0.0.1
export APP_PORT=8000
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/periodicals
```

У Docker Compose використовується:

```text
DATABASE_URL=postgresql://postgres:postgres@db:5432/periodicals
```

## Основні маршрути

| Method | Path | Опис |
|---|---|---|
| `GET` | `/login` | Сторінка входу |
| `POST` | `/login` | Обробка форми входу |
| `GET` | `/logout` | Вихід із системи |
| `GET` | `/publications` | Каталог видань |
| `GET` | `/publications/new` | Форма створення видання |
| `POST` | `/publications/create` | Створення видання |
| `POST` | `/publications/update` | Оновлення видання |
| `POST` | `/publications/delete` | Видалення видання |
| `GET` | `/subscriptions` | Список передплат користувача |
| `POST` | `/subscriptions/create` | Оформлення передплати |
| `POST` | `/subscriptions/update` | Оновлення передплати |
| `POST` | `/subscriptions/delete` | Видалення передплати |
| `GET` | `/payment` | Сторінка платежів |
| `POST` | `/payment/create` | Реєстрація платежу |
| `POST` | `/payment/update` | Оновлення статусу платежу |
| `POST` | `/payment/delete` | Видалення платежу |
| `GET` | `/static/style.css` | CSS файл |

## Unit-тести

Запуск тестів:

```bash
python -m unittest discover -s tests
```

Або через створений virtual environment:

```bash
.venv/bin/python -m unittest discover -s tests
```

Тести покривають:

- custom router;
- parsing HTTP request;
- authentication service;
- subscription service;
- розрахунок суми передплати;
- authorization checks для платежів;
- validation помилок;
- controlled error responses у controller;
- відображення назви видання в передплатах.

## Перевірка синтаксису

```bash
python -m compileall app tests
```

Або:

```bash
.venv/bin/python -m compileall app tests
```

## SQL

Схема бази знаходиться у файлі:

```text
sql/schema.sql
```

Початкові дані знаходяться у файлі:

```text
sql/seed.sql
```

Основні таблиці:

- `users`
- `publications`
- `subscriptions`
- `payments`

## Приклади сценаріїв перевірки

### Сценарій адміністратора

1. Відкрити `/login`.
2. Увійти як `admin/password`.
3. Перейти в каталог `/publications`.
4. Натиснути `+ Додати видання`.
5. Створити нове видання.
6. Оновити існуюче видання.
7. Видалити видання.

### Сценарій читача

1. Відкрити `/login`.
2. Увійти як `reader/password`.
3. Перейти в каталог `/publications`.
4. Вибрати видання і кількість місяців.
5. Оформити передплату.
6. Перейти на `/subscriptions`.
7. Перевірити суму передплати.
8. Перейти до платежів.
9. Зареєструвати платіж.
10. Змінити статус платежу.

### Сценарій захисту

1. Вийти із системи через `/logout`.
2. Відкрити `/publications` напряму.
3. Переконатися, що сервер перенаправляє на `/login`.

## Логування

Застосунок використовує стандартний модуль `logging`.

Логуються:

- старт сервера;
- HTTP-запити;
- успішна авторизація;
- невдалі спроби входу;
- 404 маршрути;
- неперехоплені помилки request processing.

## Обмеження

- Сесії зберігаються в памʼяті процесу, тому після перезапуску контейнера потрібно увійти знову.
- Паролі збережені як SHA-256 hash для навчальної роботи. У production-системі потрібно використовувати повільний password hashing, наприклад Argon2 або bcrypt.
- Це навчальний застосунок, тому він навмисно не використовує Flask, Django, FastAPI, ORM або готові auth/routing системи.

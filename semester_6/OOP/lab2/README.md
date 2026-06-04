# Лабораторна робота 2 — Система періодичних видань

Вебдодаток для керування каталогом періодичних видань, оформлення передплат читачами та реєстрації платежів. Проєкт реалізований як два окремі компоненти: backend API та frontend SPA.

## Предметна область

Система підтримує два типи користувачів:

- `admin` — адміністратор, який веде каталог періодичних видань.
- `reader` — читач, який переглядає каталог, оформлює передплати та реєструє платежі.

Основний сценарій роботи:

1. Користувач входить у систему через login/password.
2. Backend повертає JWT access token.
3. Frontend зберігає JWT у `localStorage`.
4. Frontend надсилає захищені API-запити з header `Authorization: Bearer <token>`.
5. Backend перевіряє JWT, роль користувача та виконує CRUD-операції.
6. Дані зберігаються у PostgreSQL через SQLAlchemy ORM.

## Компоненти

| Компонент | Директорія | Призначення |
| --- | --- | --- |
| Backend API | `backend/` | JSON API, JWT auth, бізнес-логіка, ORM, migrations |
| Frontend | `frontend/` | React SPA, routing, login, protected pages, CRUD UI |
| Infrastructure | `docker-compose.yml` | PostgreSQL, backend service, frontend service |

## Технології

Backend:

- Python 3.13
- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL
- `python-jose` для JWT
- Pytest
- Uvicorn

Frontend:

- React
- TypeScript
- Vite
- React Router
- Vitest
- Testing Library

Infrastructure:

- Docker
- Docker Compose
- PostgreSQL 17 Alpine image

## Відповідність вимогам лабораторної

| Вимога | Реалізація |
| --- | --- |
| Два компоненти backend API і frontend | `backend/` та `frontend/` |
| Package manager для backend | `pip`, `backend/requirements.txt` |
| Package manager для frontend | `npm`, `frontend/package.json` |
| Backend routing framework-level | FastAPI `APIRouter` |
| Frontend routing framework-level | `react-router-dom` |
| MVC pattern для backend | routers/controllers → services → repositories → ORM models → JSON view |
| JSON як View для backend API | Pydantic response models, JSON responses |
| SQL database | PostgreSQL |
| ORM | SQLAlchemy models |
| Schema migrations | Alembic initial migration |
| JWT authentication | `POST /api/auth/login` |
| JWT authorization | FastAPI dependencies, Bearer token |
| Protected frontend pages | `ProtectedRoute`, redirect на `/login` |
| CRUD з frontend через backend API | Publications, subscriptions, payments |
| Unit/API tests backend | `backend/tests/` |
| Component/routing tests frontend | `frontend/src/App.test.tsx` |
| Logging | Backend service/auth logging |
| OOP | класи models, repositories, services, mixins, dependency classes/patterns |

## Архітектура backend

```text
Incoming HTTP Request
        |
        v
FastAPI routing / APIRouter
        |
        v
Router handler as Controller
        |
        v
Service layer
        |
        v
Repository layer
        |
        v
SQLAlchemy ORM models
        |
        v
PostgreSQL
        |
        v
JSON Response
```

Backend поділений на такі шари:

- `routers/` — HTTP routing та controller-level логіка.
- `services.py` — бізнес-логіка, перевірки доступу, розрахунок сум.
- `repositories.py` — інкапсуляція роботи з базою даних.
- `models.py` — SQLAlchemy ORM моделі.
- `schemas.py` — Pydantic DTO для request/response JSON.
- `security.py` — password hashing, JWT creation/validation.
- `dependencies.py` — FastAPI dependencies для authentication/authorization.

## Архітектура frontend

```text
Browser
  |
  v
React Router
  |
  v
ProtectedRoute / AuthContext
  |
  v
Pages and UI components
  |
  v
API client with JWT header
  |
  v
Backend API
```

Frontend реалізує:

- `/login` — сторінка входу.
- `/publications` — каталог видань, admin CRUD, reader subscription creation.
- `/subscriptions` — передплати, зміна терміну, платежі, статуси платежів.
- JWT session storage у `localStorage`.
- Redirect неавторизованого користувача на `/login`.

## OOP у проєкті

У backend використані такі елементи ООП:

- Classes: `User`, `Publication`, `Subscription`, `Payment`, `AuthService`, `PublicationService`, `SubscriptionService`, repository classes.
- Encapsulation: service classes приховують бізнес-правила, repository classes приховують database access.
- Inheritance: ORM models наслідують `Base`, `User` використовує role-related mixin.
- Polymorphism: service layer працює через repository-like об'єкти, що дозволяє підміняти їх fake implementations у unit tests.

## Дані та зв'язки

Основні сутності:

| Entity | Призначення |
| --- | --- |
| `users` | користувачі системи, ролі `admin` та `reader` |
| `publications` | каталог періодичних видань |
| `subscriptions` | передплати читачів на видання |
| `payments` | платежі за передплати |

Зв'язки:

- `users 1:N subscriptions`
- `publications 1:N subscriptions`
- `subscriptions 1:N payments`

Сума передплати розраховується у service layer:

```text
total_amount = publication.price * months
```

## API endpoints

| Method | Endpoint | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `GET` | `/api/health` | no | public | health check |
| `POST` | `/api/auth/login` | no | public | login, returns JWT |
| `GET` | `/api/publications` | yes | admin/reader | list publications |
| `POST` | `/api/publications` | yes | admin | create publication |
| `PUT` | `/api/publications/{id}` | yes | admin | update publication |
| `DELETE` | `/api/publications/{id}` | yes | admin | delete publication |
| `GET` | `/api/subscriptions` | yes | admin/reader | list subscriptions |
| `POST` | `/api/subscriptions` | yes | reader/admin | create subscription |
| `PUT` | `/api/subscriptions/{id}` | yes | owner/admin | update subscription months |
| `DELETE` | `/api/subscriptions/{id}` | yes | owner/admin | delete subscription |
| `GET` | `/api/subscriptions/{id}/payments` | yes | owner/admin | list payments |
| `POST` | `/api/subscriptions/{id}/payments` | yes | owner/admin | create payment |
| `PUT` | `/api/payments/{id}` | yes | owner/admin | update payment status |
| `DELETE` | `/api/payments/{id}` | yes | owner/admin | delete payment |

## Тестові користувачі

Seed script створює користувачів:

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `password` | `admin` |
| `reader` | `password` | `reader` |
| `olena` | `password` | `reader` |

## Структура проєкту

```text
lab2/
  backend/
    app/
      routers/
        auth.py
        publications.py
        subscriptions.py
      config.py
      database.py
      dependencies.py
      main.py
      models.py
      repositories.py
      schemas.py
      security.py
      seed.py
      services.py
    alembic/
      versions/
        001_initial_periodicals.py
    tests/
      test_api.py
      test_services.py
    .dockerignore
    .gitignore
    Dockerfile
    README.md
    requirements.txt

  frontend/
    src/
      test/
        setup.ts
      api.ts
      App.test.tsx
      App.tsx
      AuthContext.tsx
      main.tsx
      style.css
      types.ts
    .dockerignore
    .gitignore
    Dockerfile
    README.md
    package.json
    tsconfig.json
    vite.config.ts

  .gitignore
  docker-compose.yml
  pytest.ini
  README.md
```

## Запуск через Docker Compose

```bash
docker compose up --build
```

Після запуску:

| Service | URL |
| --- | --- |
| Frontend | <http://localhost:5173> |
| Backend OpenAPI | <http://localhost:8000/docs> |
| Backend health | <http://localhost:8000/api/health> |
| PostgreSQL | `localhost:5432` |

Backend container автоматично виконує:

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Зупинка:

```bash
docker compose down
```

Зупинка з видаленням database volume:

```bash
docker compose down -v
```

## Локальний запуск backend

Передумова: PostgreSQL має бути запущений, база `periodicals` має існувати.

Приклад PostgreSQL через Docker:

```bash
docker run --name periodicals-postgres \
  -e POSTGRES_DB=periodicals \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:17-alpine
```

Запуск backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/periodicals
export JWT_SECRET=local-dev-secret
export FRONTEND_ORIGIN=http://localhost:5173
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Локальний запуск frontend

```bash
cd frontend
npm install
export VITE_API_URL=http://localhost:8000/api
npm run dev
```

## Тести

Backend tests з кореня проєкту:

```bash
python3 -m pytest
```

Backend tests з директорії backend:

```bash
cd backend
python3 -m pytest
```

Frontend tests:

```bash
cd frontend
npm test
```

Frontend production build:

```bash
cd frontend
npm run build
```

Останній перевірений результат:

```text
Backend: 15 passed
Frontend: 4 passed
Frontend build: success
```

## Міграції

Initial migration знаходиться у файлі:

```text
backend/alembic/versions/001_initial_periodicals.py
```

Застосування міграцій:

```bash
cd backend
alembic upgrade head
```

Створення нової міграції після зміни SQLAlchemy models:

```bash
cd backend
alembic revision --autogenerate -m "Describe schema change"
```

## JWT flow

Login request:

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "reader",
  "password": "password"
}
```

Login response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "reader",
    "role": "reader"
  }
}
```

Protected request:

```http
GET /api/publications
Authorization: Bearer <jwt>
```

## Логування

Backend використовує standard Python logging. Логи створюються для таких подій:

- successful login;
- failed login;
- publication create/update/delete;
- subscription create/update/delete;
- payment create/update/delete/status update;
- unhandled FastAPI/server errors через framework/runtime logging.

## Репозиторії

Компоненти підготовлені як незалежні директорії з власними dependency файлами та `.gitignore`:

- `backend/requirements.txt`
- `backend/.gitignore`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/.gitignore`

Для повної відповідності вимозі лабораторної потрібно запушити `backend/` і `frontend/` у два окремі remote repositories.

## Як винести у два окремі репозиторії

Виконувати команди з кореня поточного `lab2` проєкту. Директорії `periodicals-backend` та `periodicals-frontend` не повинні існувати перед запуском відповідних команд.

Backend repository:

```bash
mkdir periodicals-backend && \
cp -R backend/. periodicals-backend/ && \
cd periodicals-backend && \
git init && \
git add . && \
git commit -m "Initial FastAPI periodicals backend" && \
git branch -M main && \
git remote add origin <BACKEND_REMOTE_URL> && \
git push -u origin main
```

Frontend repository:

```bash
mkdir periodicals-frontend && \
cp -R frontend/. periodicals-frontend/ && \
cd periodicals-frontend && \
git init && \
git add . && \
git commit -m "Initial React periodicals frontend" && \
git branch -M main && \
git remote add origin <FRONTEND_REMOTE_URL> && \
git push -u origin main
```

Після push потрібно додати у звіт або відповідь викладачу дві URL-адреси remote repositories.

## Фінальна перевірка перед здачею

```bash
python3 -m pytest
```

```bash
cd frontend
npm test
npm run build
```

```bash
docker compose up --build
```

Перевірити вручну:

1. Login як `reader / password`.
2. Перегляд каталогу.
3. Створення передплати.
4. Зміна терміну передплати.
5. Реєстрація платежу.
6. Зміна статусу платежу.
7. Видалення платежу.
8. Login як `admin / password`.
9. Створення, редагування та видалення періодичного видання.

## Troubleshooting

Якщо backend не підключається до PostgreSQL:

```bash
docker compose ps
docker compose logs db
docker compose logs backend
```

Якщо потрібно повністю перестворити базу:

```bash
docker compose down -v
docker compose up --build
```

Якщо frontend не бачить backend:

```bash
cd frontend
export VITE_API_URL=http://localhost:8000/api
npm run dev
```

Якщо JWT став невалідним після перезапуску з іншим `JWT_SECRET`, потрібно вийти з системи або очистити `localStorage` у браузері.

## Чеклист відповідності лабораторній роботі

- [x] Backend API і frontend реалізовані як два компоненти.
- [x] Backend використовує package manager `pip`.
- [x] Frontend використовує package manager `npm`.
- [x] Backend routing реалізований засобами FastAPI.
- [x] Frontend routing реалізований засобами React Router.
- [x] Backend повертає JSON responses.
- [x] MVC/API-поділ реалізований через routers/controllers, services, repositories, ORM models.
- [x] SQL database — PostgreSQL.
- [x] ORM — SQLAlchemy.
- [x] Schema migrations — Alembic.
- [x] JWT authentication endpoint є.
- [x] Protected endpoints авторизуються через JWT.
- [x] Frontend login використовує backend auth endpoint.
- [x] Protected frontend pages redirect-ять неавторизованого користувача на login.
- [x] CRUD-маніпуляції ініціюються з frontend і виконуються через backend API.
- [x] Backend має unit/API tests.
- [x] Frontend має component/routing tests.
- [x] Logging реалізований у backend service/auth layer.
- [x] Код використовує ООП: класи, наслідування, поліморфізм, інкапсуляцію.
- [ ] Backend і frontend потрібно запушити у два окремі remote repositories.

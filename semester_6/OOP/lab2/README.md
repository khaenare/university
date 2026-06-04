# Лабораторна робота 2 — Система періодичних видань

Вебдодаток складається з двох компонентів:

- `backend/` — JSON API на FastAPI.
- `frontend/` — SPA на React/Vite.

Предметна область: адміністратор веде каталог періодичних видань, читач оформлює передплату, система рахує суму до оплати та реєструє платежі.

## Відповідність вимогам

- Backend використовує менеджер пакетів `pip` і `backend/requirements.txt`.
- Frontend використовує менеджер пакетів `npm` і `frontend/package.json`.
- Backend routing реалізований засобами FastAPI `APIRouter`.
- Backend побудований як MVC/API-поділ: routers/controllers → services → repositories → ORM models → DB; View повертається у форматі JSON.
- SQL база даних — PostgreSQL.
- ORM — SQLAlchemy.
- Міграції — Alembic, initial migration у `backend/alembic/versions/001_initial_periodicals.py`.
- JWT authentication — endpoint `POST /api/auth/login`, protected endpoints через `Authorization: Bearer <token>`.
- Авторизація ролей: `admin` керує каталогом, `reader` оформлює передплати й платежі.
- Frontend routing — `react-router-dom`.
- Frontend має `/login`, protected routes і redirect неавторизованого користувача на login.
- Логування реалізоване у service/auth layer і FastAPI startup-конфігурації.
- Unit/API tests додані для backend, component/routing tests — для frontend.

## Структура

```text
lab2/
  backend/
    app/
      routers/          # controllers/routing
      config.py
      database.py
      dependencies.py   # JWT dependencies
      models.py         # SQLAlchemy ORM models
      repositories.py   # DB access abstraction
      schemas.py        # Pydantic JSON schemas
      security.py       # password hash + JWT
      services.py       # business logic
      main.py
      seed.py
    alembic/
    tests/
    requirements.txt

  frontend/
    src/
      api.ts
      AuthContext.tsx
      App.tsx
      main.tsx
    package.json

  docker-compose.yml
```

## API endpoints

- `POST /api/auth/login`
- `GET /api/publications`
- `POST /api/publications` — admin
- `PUT /api/publications/{id}` — admin
- `DELETE /api/publications/{id}` — admin
- `GET /api/subscriptions`
- `POST /api/subscriptions`
- `PUT /api/subscriptions/{id}`
- `DELETE /api/subscriptions/{id}`
- `GET /api/subscriptions/{id}/payments`
- `POST /api/subscriptions/{id}/payments`
- `PUT /api/payments/{id}`
- `DELETE /api/payments/{id}`

## Тестові користувачі

Seed створює користувачів:

- `admin` / `password`
- `reader` / `password`
- `olena` / `password`

## Запуск через Docker Compose

```bash
docker compose up --build
```

- Frontend: <http://localhost:5173>
- Backend OpenAPI: <http://localhost:8000/docs>
- Healthcheck: <http://localhost:8000/api/health>

Backend container виконує:

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Локальний запуск backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/periodicals
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Локальний запуск frontend

```bash
cd frontend
npm install
npm run dev
```

## Тести

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Репозиторії

Компоненти підготовлені як незалежні директорії з власними package/dependency файлами та `.gitignore`. Для повної відповідності вимозі лабораторної їх можна винести у два окремі remote repositories: один для `backend/`, інший для `frontend/`.

## Фінальна перевірка перед здачею

З кореня проєкту:

```bash
python3 -m pytest
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

Повний запуск:

```bash
docker compose up --build
```

Після запуску перевірити:

- Frontend: <http://localhost:5173>
- Backend OpenAPI: <http://localhost:8000/docs>
- Backend health: <http://localhost:8000/api/health>

## Як винести у два окремі репозиторії

### Backend repository

Виконувати з кореня поточного `lab2` проєкту. Цільова директорія `periodicals-backend` не повинна існувати перед запуском команди.

```bash
mkdir periodicals-backend && \
cp -R backend/* periodicals-backend/ && \
cp backend/.gitignore backend/.dockerignore periodicals-backend/ && \
cd periodicals-backend && \
git init && \
git add . && \
git commit -m "Initial FastAPI periodicals backend" && \
git branch -M main && \
git remote add origin <BACKEND_REMOTE_URL> && \
git push -u origin main
```

### Frontend repository

Виконувати з кореня поточного `lab2` проєкту. Цільова директорія `periodicals-frontend` не повинна існувати перед запуском команди.

```bash
mkdir periodicals-frontend && \
cp -R frontend/* periodicals-frontend/ && \
cp frontend/.gitignore frontend/.dockerignore periodicals-frontend/ && \
cd periodicals-frontend && \
git init && \
git add . && \
git commit -m "Initial React periodicals frontend" && \
git branch -M main && \
git remote add origin <FRONTEND_REMOTE_URL> && \
git push -u origin main
```

Після push потрібно додати у відповідь викладачу дві URL-адреси remote repositories.

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
- [ ] Backend і frontend потрібно запушити у два окремі remote repositories.

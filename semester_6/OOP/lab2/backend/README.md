# Periodicals Backend API

FastAPI backend for the Periodicals subscription system.

## Stack

- Python 3.13
- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL
- JWT auth with `python-jose`
- Pytest

## Environment

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/periodicals
JWT_SECRET=change-me
FRONTEND_ORIGIN=http://localhost:5173
```

## Local setup

Prerequisite: PostgreSQL must be running and the `periodicals` database must exist.
For example, with Docker:

```bash
docker run --name periodicals-postgres \
  -e POSTGRES_DB=periodicals \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:17-alpine
```

Then run the backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

API docs: <http://localhost:8000/docs>

## Tests

```bash
python3 -m pytest
```

## Test users

- `admin` / `password`
- `reader` / `password`
- `olena` / `password`

## Main endpoints

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

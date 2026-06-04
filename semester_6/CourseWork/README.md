# Warehouse Coursework Local Run Guide

This solution is implemented as two separate repositories, but they run together as one integrated system:

- `warehouse-backend`
- `warehouse-frontend`

## 1) Start PostgreSQL

Start Docker Desktop first. Then run the local PostgreSQL container:

```bash
docker start warehouse-postgres
```

If the container does not exist yet, create it once:

```bash
docker run --name warehouse-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=warehouse_db \
  -p 5432:5432 \
  -d postgres:16
```

## 2) Start backend

```bash
cd warehouse-backend
cp .env.example .env
npm install
npx prisma generate
npx prisma db push
npm run db:seed
npm run dev
```

Backend runs on `http://localhost:3001`.

## 3) Start frontend

```bash
cd warehouse-frontend
cp .env.example .env.local
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`.

## 4) Open application

- Home: `http://localhost:3000`
- Reports: `http://localhost:3000/reports`
- Receipts: `http://localhost:3000/receipts`
- Write-Offs: `http://localhost:3000/writeoffs`
- Production Orders: `http://localhost:3000/production-orders`

## Notes

- Use the `warehouse-postgres` Docker container for local backend data.
- All UI and code comments are in English.

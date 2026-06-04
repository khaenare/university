## Warehouse Backend

Backend service for the warehouse coursework project.

Stack: Next.js API routes, TypeScript, Prisma ORM, PostgreSQL.

## Getting Started

Run the development server:

```bash
npm run dev
```

Backend runs on [http://localhost:3001](http://localhost:3001).

## Notes

- This repository contains backend code only.
- Frontend must run from a separate repository (`warehouse-frontend`).
- All user-facing text and comments in this project must be in English.

## Localhost workflow

1. Start Docker Desktop and PostgreSQL locally:

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

2. Prepare the database schema and demo data:

   ```bash
   npm install
   cp .env.example .env
   npx prisma generate
   npx prisma db push
   npm run db:seed
   ```

3. Start backend in this repository.
4. Start frontend in `warehouse-frontend` on port 3000.

## Environment setup

1. Copy `.env.example` to `.env`.
2. Update `DATABASE_URL` if your local PostgreSQL credentials differ.

## Prisma commands

For local schema sync on a fresh demo database:

```bash
npx prisma generate
npx prisma db push
```

For migration development instead of `db push`:

```bash
npx prisma migrate dev
```

Seed demo data after the schema exists:

```bash
npm run db:seed
```

Default local seed credentials:

- Email: `admin@localhost`
- Password: `admin12345`

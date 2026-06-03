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

1. Start PostgreSQL locally.
2. Start backend in this repository.
3. Start frontend in `warehouse-frontend` on port 3000.

## Environment setup

1. Copy `.env.example` to `.env`.
2. Update `DATABASE_URL` if your local PostgreSQL credentials differ.

## Prisma commands

```bash
npx prisma generate
npx prisma migrate dev
npm run db:seed
```

Default local seed credentials:

- Email: `admin@localhost`
- Password: `admin12345`

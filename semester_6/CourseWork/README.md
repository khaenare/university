# Warehouse Coursework Local Run Guide

This solution is implemented as two separate repositories, but they run together as one integrated system:

- `warehouse-backend`
- `warehouse-frontend`

## 1) Start backend

```bash
cd warehouse-backend
cp .env.example .env
npm install
npx prisma generate
npm run dev
```

Backend runs on `http://localhost:3001`.

## 2) Start frontend

```bash
cd warehouse-frontend
cp .env.example .env.local
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`.

## 3) Open application

- Home: `http://localhost:3000`
- Reports: `http://localhost:3000/reports`
- Receipts: `http://localhost:3000/receipts`
- Write-Offs: `http://localhost:3000/writeoffs`
- Production Orders: `http://localhost:3000/production-orders`

## Notes

- Use PostgreSQL locally for backend data.
- All UI and code comments are in English.

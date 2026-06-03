## Warehouse Frontend

Frontend application for the warehouse coursework project.

Stack: React, Next.js, TypeScript.

## Getting Started

Run the development server:

```bash
npm run dev
```

Frontend runs on [http://localhost:3000](http://localhost:3000).

## Notes

- This repository contains frontend code only.
- Backend must run from a separate repository (`warehouse-backend`) on port 3001.
- All user-facing text and comments in this project must be in English.

## Environment setup

1. Copy `.env.example` to `.env.local`.
2. Set `NEXT_PUBLIC_API_BASE_URL` to your backend URL.

## Localhost workflow

1. Start backend in `warehouse-backend`.
2. Start frontend in this repository.
3. Open the frontend in your browser.

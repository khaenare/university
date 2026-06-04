# Periodicals Frontend

React/Vite frontend for the Periodicals subscription system.

## Stack

- React
- TypeScript
- Vite
- React Router
- JWT auth stored in `localStorage`
- Vitest + Testing Library

## Environment

```bash
VITE_API_URL=http://localhost:8000/api
```

## Local setup

```bash
npm install
npm run dev
```

Frontend URL: <http://localhost:5173>

## Tests and build

```bash
npm test
npm run build
```

## Implemented pages

- `/login` — login form using backend JWT auth endpoint.
- `/publications` — protected catalog page.
- `/subscriptions` — protected subscriptions and payments page.

If there is no JWT session, protected pages redirect to `/login`.

## Test users

- `admin` / `password` — publication create/update/delete.
- `reader` / `password` — subscriptions and payments.

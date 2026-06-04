# Повна витримка по проєкту Warehouse Coursework

Дата аналізу: 03.06.2026  
Проєкт: `CourseWork`  
Основні частини системи: `warehouse-backend` і `warehouse-frontend`  
Мова опису: українська з використанням стандартних English technology/domain terms: `frontend`, `backend`, `API`, `JWT`, `BOM`, `InventoryTransaction`, `ProductionOrder`, `CostSnapshot` тощо.

> Примітка щодо повноти: цей документ складено на основі фактичного аналізу README, package/config files, Prisma schema, seed script, backend API routes, frontend pages, shared libraries and tests. Він описує всі виявлені основні можливості проєкту. Якщо якась функція не згадується в коді або документації, вона не додавалась як припущення.

## 1. Призначення проєкту та предметна область

Проєкт є навчальною web-based інформаційною системою для управління складськими та виробничими процесами. Система моделює типовий workflow невеликого виробничого складу: ведення довідників товарів і постачальників, реєстрація надходжень, контроль залишків, списання товарів, опис виробничих рецептів, створення production orders, розрахунок собівартості готової продукції та формування звітності.

Предметна область — warehouse accounting and production accounting. У системі є два типи продуктів:

- `COMPONENT` — комплектуючі, матеріали або деталі, які закуповуються та споживаються у виробництві;
- `FINISHED` — готова продукція, що може бути вироблена за BOM-рецептом або оприбуткована через receipt.

Ключова ідея реалізації: усі зміни залишків фіксуються у журналі `InventoryTransaction`. Надходження та випуск готової продукції збільшують залишок, а списання та виробниче споживання компонентів зменшують його. Завдяки цьому з одного журналу можна отримати current stock balance, inventory movement history and valuation reports.

Система орієнтована на локальний запуск для демонстрації курсової роботи. За README: backend працює на `http://localhost:3001`, frontend — на `http://localhost:3000`, база даних — PostgreSQL.

## 2. High-level architecture

Архітектура складається з двох окремих застосунків:

1. **`warehouse-backend`** — backend service на Next.js API Routes. Він відповідає за REST-like API, Prisma ORM, PostgreSQL access, authentication/authorization, validation, business logic, transactions, cost calculation and reports.
2. **`warehouse-frontend`** — frontend application на Next.js/React. Він відповідає за UI, login/session handling, role-based navigation, operation forms, dashboard and reports visualization.

Загальна схема:

```text
User
  ↓
Frontend: Next.js / React, localhost:3000
  ↓ HTTP requests + Authorization: Bearer JWT
Backend: Next.js API Routes, localhost:3001
  ↓ Prisma ORM
PostgreSQL database
```

Backend має CORS middleware для API-запитів з `http://localhost:3000`. Frontend отримує адресу API з `NEXT_PUBLIC_API_BASE_URL`, а якщо вона не задана в development, використовує `http://localhost:3001`.

## 3. Technology stack

### Backend stack

- `Next.js 16.2.6` — API layer через App Router route handlers.
- `TypeScript` — strict typed backend code.
- `Prisma ORM 6.19.0` — schema, migrations, database client.
- `PostgreSQL` — relational storage.
- `bcryptjs` — password hashing.
- `jsonwebtoken` — JWT access/refresh tokens.
- `tsx` + Node.js built-in test runner — unit/API tests.
- `ESLint` — linting.

### Frontend stack

- `Next.js 16.2.6` — frontend app.
- `React 19.2.4` — interactive UI pages.
- `TypeScript` — typed API client and form payloads.
- `CSS` через global styles/classes.
- `tsx` + Node.js test runner — tests for form payload builders.
- `ESLint` — linting.

## 4. Repository structure

Кореневий каталог `CourseWork` містить:

- `README.md` — local run guide для всієї системи.
- `DEMO_SCRIPT.md` — сценарій демонстрації: receipt → production order → write-off → reports.
- `COURSEWORK_PROJECT_OVERVIEW.md` — цей аналітичний файл для курсового звіту.
- `warehouse-backend/` — backend service.
- `warehouse-frontend/` — frontend application.
- `.opencode/`, `opencode.json` — службові файли середовища, не належать до бізнес-логіки.

### `warehouse-backend/`

- `package.json` — scripts: `dev`, `build`, `start`, `lint`, `db:seed`, `test`; dependencies.
- `.env.example` — `DATABASE_URL`, `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`.
- `prisma/schema.prisma` — database schema.
- `prisma/migrations/` — SQL migrations.
- `prisma/seed.ts` — demo users and warehouse data.
- `src/app/api/` — API routes.
- `src/lib/` — reusable backend logic: auth, authorization, validation, inventory, costing, query/date helpers.
- `src/middleware.ts` — CORS for `/api/:path*`.

### `warehouse-frontend/`

- `package.json` — scripts: `dev`, `build`, `start`, `lint`, `test`.
- `.env.example` — `NEXT_PUBLIC_API_BASE_URL`.
- `src/app/` — pages: dashboard, stock, receipts, writeoffs, production-orders, production-recipes, products, suppliers, reports.
- `src/components/auth-shell.tsx` — global app shell, login/logout, sidebar, role-based access.
- `src/lib/api.ts` — typed API client.
- `src/lib/form-payloads.ts` — client-side form validation and payload construction.

## 5. Data model and storage

Data model описана в `warehouse-backend/prisma/schema.prisma`.

### Authentication domain

- `User`: email, `passwordHash`, `role`, timestamps, relations to `RefreshToken` and `AuditLog`.
- `RefreshToken`: hashed refresh token, userId, expiration.
- `UserRole`: `ADMIN`, `MANAGER`, `OPERATOR`, `VIEWER`.

Фактично в UI та role checks активно використовуються `ADMIN` і `MANAGER`. `OPERATOR` і `VIEWER` уже присутні в schema, але не мають повної frontend-навігації та окремої permission model. Це потенційна точка розвитку.

### Master data

- `Supplier`: supplier name and contact fields.
- `Product`: SKU, name, unit, type, `isActive`.

### Production recipe / BOM

- `Bom`: recipe for one finished product. У schema є `@@unique([finishedProductId])`, тобто один finished product має одну BOM.
- `BomItem`: component and quantity per one unit of finished product.

### Warehouse documents and operations

- `Receipt`: incoming supply document.
- `ReceiptLine`: product, quantity, purchase price.
- `WriteOff`: write-off document with reason.
- `WriteOffLine`: product and quantity to issue from stock.
- `ProductionOrder`: finished product and output quantity.
- `ProductionOrderItem`: actual component consumption lines.
- `InventoryTransaction`: central ledger of stock movements.
- `CostSnapshot`: historical production cost snapshot with JSON calculation details.
- `AuditLog`: model exists, but analyzed routes do not write audit records yet.

### Enumerations

- `ProductType`: `COMPONENT`, `FINISHED`.
- `TransactionType`: `RECEIPT`, `ISSUE_SALE`, `ISSUE_PRODUCTION`, `PRODUCTION_OUTPUT`, `ADJUSTMENT`.
- `WriteOffReason`: `SALE`, `PRODUCTION`; however current write-off UI/backend validation accepts only `SALE` for manual write-offs.

## 6. Backend API capabilities

### 6.1 Authentication API

- `POST /api/auth/login`
  - accepts email/password;
  - checks password with `bcryptjs`;
  - returns `accessToken`, `refreshToken`, and user object;
  - stores hashed refresh token in DB.

- `GET /api/auth/me`
  - reads Bearer access token;
  - verifies JWT;
  - returns current user data.

- `POST /api/auth/refresh`
  - verifies refresh token;
  - checks token hash in DB;
  - deletes old refresh token and creates a new one;
  - returns new access and refresh token.

- `POST /api/auth/logout`
  - deletes stored refresh token by hash;
  - returns success message.

Important detail: backend supports refresh flow, but frontend currently does not automatically call refresh on access-token expiration. On `401`, frontend clears local session and asks user to sign in again.

### 6.2 Products API

- `GET /api/products` — list all products, allowed for `ADMIN` and `MANAGER`.
- `POST /api/products` — create product, allowed for `ADMIN`.
- `GET /api/products/[id]` — get product by id.
- `PATCH /api/products/[id]` — update SKU/name/unit/type/isActive, allowed for `ADMIN`.
- `DELETE /api/products/[id]` — delete product, allowed for `ADMIN`.

Deletion is protected by database constraints: if product has related inventory records, backend returns conflict message `Cannot delete product with related inventory records.`

### 6.3 Suppliers API

- `GET /api/suppliers` — list suppliers.
- `POST /api/suppliers` — create supplier, allowed for `ADMIN`.
- `GET /api/suppliers/[id]` — get supplier by id.
- `PATCH /api/suppliers/[id]` — update name/contact fields, allowed for `ADMIN`.
- `DELETE /api/suppliers/[id]` — delete supplier, allowed for `ADMIN`.

Deletion is blocked if supplier has related receipts.

### 6.4 BOM / production recipes API

- `GET /api/bom` — list recipes with finished product and components.
- `POST /api/bom` — create recipe, allowed for `ADMIN`.
- `GET /api/bom/[id]` — get recipe by id.
- `PATCH /api/bom/[id]` — update finished product and/or component list, allowed for `ADMIN`.
- `DELETE /api/bom/[id]` — delete recipe, allowed for `ADMIN`.

Validation rules:

- finished product must exist and have `FINISHED` type;
- every component must exist and have `COMPONENT` type;
- component list must be non-empty;
- component ids must be unique;
- component quantities must be greater than zero;
- only one BOM per finished product is allowed.

### 6.5 Receipts API

- `GET /api/receipts` — list receipt history with supplier and product lines.
- `POST /api/receipts` — create incoming receipt, allowed for `ADMIN` and `MANAGER`.
- `GET /api/receipts/[id]` — get one receipt.

When creating receipt, backend:

1. validates supplier id, invoice number, ISO UTC invoice date and lines;
2. verifies supplier and products exist;
3. creates `Receipt` and `ReceiptLine` records;
4. creates positive `InventoryTransaction` records with type `RECEIPT`, quantity and unit cost equal to purchase price.

### 6.6 Write-offs API

- `GET /api/writeoffs` — list write-off history.
- `POST /api/writeoffs` — create write-off, allowed for `ADMIN` and `MANAGER`.
- `GET /api/writeoffs/[id]` — get one write-off.

Current manual write-off reason is `SALE`. When creating write-off:

1. backend validates reason and lines;
2. verifies products exist;
3. checks sufficient stock using `assertSufficientStock`;
4. creates `WriteOff` and `WriteOffLine`;
5. creates negative `InventoryTransaction` records with type `ISSUE_SALE`.

The operation uses `Serializable` transaction isolation.

### 6.7 Production orders API

- `GET /api/production-orders` — list production orders with finished product and consumed components.
- `POST /api/production-orders` — create production order, allowed for `ADMIN` and `MANAGER`.
- `GET /api/production-orders/[id]` — get one production order.

Production order workflow:

1. Validate finished product id and output quantity.
2. Check product exists and has `FINISHED` type.
3. Load BOM for the finished product.
4. Calculate component requirements: `BOM quantity per unit * outputQuantity`.
5. Check that all components exist and have `COMPONENT` type.
6. Calculate current stock for each component from `InventoryTransaction` ledger.
7. If stock is insufficient, return detailed message with possible output and missing components.
8. Calculate production cost through weighted average component cost.
9. Create:
   - `ProductionOrder`;
   - `ProductionOrderItem` component lines;
   - positive `InventoryTransaction` with type `PRODUCTION_OUTPUT`;
   - negative `InventoryTransaction` records with type `ISSUE_PRODUCTION`;
   - `CostSnapshot` with calculation details.

This route also uses `Serializable` transaction isolation.

### 6.8 Stock and reports API

- `GET /api/stock/balance`
  - returns products with current quantity calculated as sum of inventory transactions.

- `GET /api/reports/stock-valuation`
  - returns quantity, unit cost, valuation per product and total valuation;
  - unit cost is selected from latest transaction with cost among `RECEIPT` and `PRODUCTION_OUTPUT`.

- `GET /api/reports/production-cost`
  - returns `CostSnapshot` data;
  - supports `from`, `to`, `limit` query params;
  - `limit` is bounded to max 100.

- `GET /api/reports/movements`
  - returns inventory movement ledger;
  - supports `from`, `to`, `productId`, `limit`.

- `GET /api/costing/product/[id]/current`
  - calculates current cost for one unit of a finished product based on BOM and weighted average component cost.

## 7. Frontend capabilities

### 7.1 AuthShell and navigation

`src/components/auth-shell.tsx` provides:

- login form with seeded demo credentials;
- access/refresh token storage in `localStorage`;
- session check through `/api/auth/me`;
- logout through `/api/auth/logout`;
- sidebar navigation grouped into Overview, Operations, Production, Directories, Reports;
- role-based visibility of menu items;
- `Access denied` screen when a route is not allowed for current role.

Navigation permissions in UI:

- `ADMIN`: dashboard, stock, receipts, write-offs, production orders, production recipes, products, suppliers, reports.
- `MANAGER`: dashboard, stock, receipts, write-offs, production orders, reports.

### 7.2 Dashboard `/`

Dashboard loads:

- stock valuation;
- latest inventory movements;
- latest production cost snapshots.

It displays:

- total stock valuation;
- count of products in stock;
- low-stock items;
- top products by valuation;
- recent movements;
- latest production costs.

### 7.3 Stock page `/stock`

The stock page uses stock valuation data and provides client-side:

- search by SKU/name;
- filtering by product type: all/components/finished;
- filtering by availability: all/in stock/low stock/empty;
- sorting by valuation, quantity, unit cost, SKU or name;
- ascending/descending switch.

### 7.4 Products page `/products`

Provides product catalog management for `ADMIN`:

- list products;
- create product;
- edit product;
- delete product;
- fields: SKU, name, unit, type, active flag.

### 7.5 Suppliers page `/suppliers`

Provides supplier management for `ADMIN`:

- list suppliers;
- create supplier;
- edit supplier;
- delete supplier;
- fields: name, contactName, contactEmail, contactPhone, address.

### 7.6 Receipts page `/receipts`

Provides receiving workflow:

- loads suppliers, products and receipt history;
- creates receipt with supplier, invoice number, invoice date and one or more lines;
- validates required fields and positive quantities on frontend;
- converts browser datetime input to ISO string;
- prevents duplicate products in one receipt.

### 7.7 Write-offs page `/writeoffs`

Provides manual stock issue workflow:

- loads products and write-off history;
- creates a `SALE` write-off for a selected product and quantity;
- validates product selection and positive quantity.

### 7.8 Production recipes page `/production-recipes`

Provides production recipe management for `ADMIN`:

- list existing recipes;
- create a new `FINISHED` product directly from the recipe page;
- create a BOM recipe for selected finished product;
- add/remove component lines;
- validate unique components and positive quantities.

Important nuance: backend supports PATCH/DELETE for BOM, but current frontend page mainly exposes create/list workflow, not full editing/deleting UI for recipes.

### 7.9 Production orders page `/production-orders`

Provides production execution workflow:

- loads finished products and production history;
- creates production order for selected finished product and quantity;
- backend automatically expands BOM into component consumption lines;
- frontend displays operation result/history.

### 7.10 Reports pages

- `/reports` — report center with links.
- `/reports/stock-valuation` — current quantities, unit costs, valuation bars, summary and detail table.
- `/reports/production-cost` — production cost snapshots.
- `/reports/movements` — inventory movement ledger; frontend additionally filters movements by movement type.

## 8. Data flow scenarios

### Scenario 1: Incoming receipt

```text
Receipts UI
  → buildReceiptPayload(formData)
  → POST /api/receipts
  → backend validation
  → Receipt + ReceiptLine
  → InventoryTransaction(RECEIPT, +quantity, unitCost=purchasePrice)
  → stock balance and valuation update
```

### Scenario 2: Production order

```text
Production Orders UI
  → POST /api/production-orders
  → backend loads FINISHED product and BOM
  → calculates component requirements
  → checks component stock
  → calculates weighted average cost
  → creates ProductionOrder, ProductionOrderItems
  → creates PRODUCTION_OUTPUT for finished product
  → creates ISSUE_PRODUCTION for components
  → creates CostSnapshot
```

### Scenario 3: Sale write-off

```text
Write-offs UI
  → buildWriteOffPayload(formData)
  → POST /api/writeoffs
  → stock availability check
  → WriteOff + WriteOffLine
  → InventoryTransaction(ISSUE_SALE, -quantity)
```

### Scenario 4: Reporting

```text
Reports UI
  → authenticated GET requests
  → Prisma queries/groupBy/findMany
  → backend serializes Decimal values to strings
  → frontend renders tables/cards/charts
```

## 9. Important algorithms and implementation patterns

### 9.1 Stock balance calculation

Stock is calculated from movement ledger:

```text
currentStock(product) = sum(InventoryTransaction.quantity where productId = product.id)
```

This ledger-based design is a strong accounting pattern because it preserves history and supports reporting.

### 9.2 Sufficient stock validation

`src/lib/inventory.ts` provides:

- `getProductStock(tx, productId)` — sums quantities for product;
- `assertSufficientStock(tx, productId, issueQuantity)` — throws error if operation would make stock negative.

For production, backend also calculates shortage details and possible production quantity.

### 9.3 Weighted average cost

`src/lib/costing.ts` calculates component average cost from receipt lines:

```text
averageUnitCost = sum(receiptQuantity * purchasePrice) / sum(receiptQuantity)
```

Production cost:

```text
componentLineCost = requiredComponentQuantity * averageUnitCost
totalProductionCost = sum(componentLineCost)
unitProductionCost = totalProductionCost / outputQuantity
```

If component has no receipt history, cost calculation fails with validation error. This protects reports from unsupported cost assumptions.

### 9.4 Cost snapshots

When production order is created, backend stores `CostSnapshot` with:

- `productionOrderId`;
- `finishedProductId`;
- `totalCost`;
- `unitCost`;
- JSON details: output quantity and component-level costs.

This is important because historical production cost remains stable even if later purchase prices change.

### 9.5 Transactions and isolation

Critical operations use Prisma transactions:

- receipts: document + inventory movements;
- write-offs: stock check + document + negative movements;
- production orders: stock checks + order + component issues + output + cost snapshot.

Write-offs and production orders use `Serializable` isolation level to reduce concurrency risks.

### 9.6 Two-level validation

Validation exists both on frontend and backend:

- frontend gives quick user feedback;
- backend remains source of truth and protects data integrity.

Examples: non-empty lines, positive quantities, unique products/components, ISO UTC invoice date, correct product types for BOM and production.

## 10. Configuration, build, run and testing

### Backend setup

```bash
cd warehouse-backend
cp .env.example .env
npm install
npx prisma generate
npx prisma migrate dev
npm run db:seed
npm run dev
```

Backend URL: `http://localhost:3001`.

Environment example:

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/warehouse_db?schema=public"
JWT_ACCESS_SECRET="replace-with-local-access-secret"
JWT_REFRESH_SECRET="replace-with-local-refresh-secret"
```

Seeded credentials:

- `admin@localhost / admin12345`
- `manager@localhost / manager12345`

Seed also creates suppliers, component products, finished products, BOM recipes, receipts, production orders, write-offs and cost snapshots.

### Frontend setup

```bash
cd warehouse-frontend
cp .env.example .env.local
npm install
npm run dev
```

Frontend URL: `http://localhost:3000`.

Environment example:

```env
NEXT_PUBLIC_API_BASE_URL="http://localhost:3001"
```

### Build and lint

Both apps support:

```bash
npm run build
npm run lint
```

### Tests

Backend:

```bash
cd warehouse-backend
npm test
```

The backend test script covers validation libraries and many route handlers: products, BOM, receipts, stock balance, write-offs, production orders, current costing, stock valuation, production cost and movements reports.

Frontend:

```bash
cd warehouse-frontend
npm test
```

Frontend tests cover `form-payloads.ts`: receipt payloads, duplicate validation, write-off payloads, production order payloads and production recipe payloads.

## 11. Demo workflow for coursework defense

Recommended demo based on `DEMO_SCRIPT.md`:

1. Start PostgreSQL, backend and frontend.
2. Run migrations and seed if needed.
3. Log in as admin or manager.
4. Open Dashboard and explain key indicators.
5. Open Receipts and create incoming supply.
6. Open Production Orders and create finished product output.
7. Open Write-Offs and create `SALE` issue.
8. Open Reports:
   - Stock Valuation;
   - Production Cost;
   - Inventory Movements.
9. Explain how movements reflect receipt, component consumption, production output and sale issue.

## 12. Strengths of the project

1. Clear separation between frontend and backend.
2. Realistic warehouse/production domain model.
3. Ledger-based inventory accounting through `InventoryTransaction`.
4. Transactional operations for multi-table business processes.
5. Role-based JWT authorization.
6. Historical production cost snapshots.
7. Validation on both client and server sides.
8. Demo seed data for fast presentation.
9. Multiple practical reports.
10. Tests for important validation, route and reporting behavior.

## 13. Limitations and possible improvements

1. **Automatic refresh flow on frontend is missing.** Backend has `/api/auth/refresh`, but frontend currently clears session on `401`.
2. **Roles can be expanded.** `OPERATOR` and `VIEWER` exist in schema but are not fully implemented in UI/permissions.
3. **Write-off reasons are limited in UI.** Prisma enum includes `PRODUCTION`, but manual write-offs accept only `SALE`.
4. **Inventory valuation is simplified.** Current report uses latest known unit cost; advanced FIFO/LIFO/current weighted average valuation could be added.
5. **AuditLog is not used by routes.** The model exists, but operations are not logged into it.
6. **No Docker/deployment setup was found.** Docker Compose could simplify PostgreSQL + apps launch.
7. **No user management UI.** Users are seeded, not managed through frontend.
8. **Server-side pagination is limited.** Some reports have `limit`, but directories/history pages load full lists.
9. **BOM editing/deleting exists in backend but not fully exposed in frontend UI.** Current recipe page focuses on create/list.
10. **No end-to-end tests.** Playwright/Cypress could verify full workflow login → receipt → production → write-off → reports.

## 14. Suggested coursework report outline

1. **Вступ**
   - актуальність warehouse accounting;
   - мета роботи;
   - основні завдання.

2. **Аналіз предметної області**
   - складський облік;
   - виробничі рецепти/BOM;
   - складські рухи;
   - собівартість готової продукції.

3. **Постановка задачі**
   - functional requirements;
   - non-functional requirements;
   - ролі користувачів.

4. **Обґрунтування вибору технологій**
   - Next.js, React, TypeScript;
   - Prisma ORM and PostgreSQL;
   - JWT and bcrypt;
   - testing tools.

5. **Архітектура системи**
   - frontend/backend split;
   - HTTP API interaction;
   - authentication and authorization;
   - CORS and local deployment.

6. **Проєктування бази даних**
   - users and tokens;
   - suppliers and products;
   - receipts and write-offs;
   - BOM and production orders;
   - inventory transactions and cost snapshots.

7. **Реалізація backend**
   - API routes;
   - validation;
   - transactions;
   - stock calculation;
   - weighted average cost;
   - reports.

8. **Реалізація frontend**
   - AuthShell;
   - dashboard;
   - directories;
   - warehouse operation pages;
   - production pages;
   - reports.

9. **Тестування**
   - backend route/library tests;
   - frontend payload tests;
   - demo scenario checks.

10. **Демонстрація роботи системи**
    - local setup;
    - seeded users;
    - full warehouse workflow.

11. **Оцінка результатів і обмеження**
    - strengths;
    - limitations;
    - possible future improvements.

12. **Висновки**
    - досягнення мети;
    - практична цінність реалізованої системи.

## 15. Short summary for report

Розроблений проєкт є full-stack web application для складського та виробничого обліку. Backend побудовано на Next.js API Routes, TypeScript, Prisma ORM and PostgreSQL; frontend — на Next.js, React and TypeScript. Система підтримує login/logout, role-based access, product and supplier directories, receipts, sale write-offs, BOM recipes, production orders, stock balance and analytical reports. Центральною частиною обліку є `InventoryTransaction`, через який розраховуються залишки та історія рухів. Для виробництва реалізовано автоматичне списання компонентів за BOM, випуск finished product, weighted average cost calculation and `CostSnapshot` storage. Проєкт має seed data and tests, тому підходить для демонстрації та опису в курсовій роботі.

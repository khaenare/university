# Coursework Demo Script

## Goal

Show the full warehouse flow from receipt creation to reporting.

## Prerequisites

1. Backend is running on `http://localhost:3001`.
2. Frontend is running on `http://localhost:3000`.
3. Database has at least one supplier, one component product, one finished product, and BOM configured.

## Demo Steps

1. Open frontend home page (`/`).
2. Open **Receipts** page.
3. Create a receipt for a component product with quantity and purchase price.
4. Confirm success message and new row in receipts list.
5. Open **Production Orders** page.
6. Create a production order for a finished product.
7. Confirm success message and new row in production orders list.
8. Open **Write-Offs** page.
9. Create a write-off (reason `SALE`) for a product with available stock.
10. Confirm success message and new row in write-offs list.
11. Open **Reports** page.
12. Explain report sections:
    - Stock valuation
    - Production cost
    - Inventory movements
13. Highlight that movements reflect receipt, production output/consumption, and write-off operations.

## Key Points to Explain

- Operations are handled by separate backend and frontend repositories.
- Backend validates inputs and applies atomic transactions.
- Production flow consumes BOM components and creates finished output.
- Cost snapshots are stored for production events and used in reports.

# Stockroom

Stockroom is a production-minded inventory and order management MVP for small businesses. It combines a FastAPI modular monolith, PostgreSQL, JWT authentication, transactional order creation, idempotency, audit logging, and a polished React dashboard.

## Features
- JWT registration, login, logout, protected routes, and authenticated API access.
- Product, customer, and order management with soft deletes.
- Unique SKU and customer email constraints enforced at the database layer.
- Server-side inventory protection and transactional order creation.
- `Idempotency-Key` support for retry-safe order creation.
- Audit logs for product, customer, and order lifecycle events.
- Request correlation IDs via `X-Request-ID` and JSON structured logging.
- Dashboard metrics for products, customers, orders, inventory value, recent orders, and stock alerts.
- Professional tables with search, sorting, pagination, loading, empty, error, and success states.

## Architecture
```mermaid
flowchart LR
  U[User] --> F[React + Vite]
  F -->|JWT REST API| B[FastAPI Modular Monolith]
  B --> S[Services]
  S --> DB[(PostgreSQL)]
  B --> L[JSON Logs + X-Request-ID]
```

```mermaid
flowchart TB
  API[API Routers] --> Auth[Auth Dependencies]
  API --> Services[Business Services]
  Services --> Models[SQLAlchemy Models]
  Models --> DB[(PostgreSQL)]
  Services --> Audit[Audit Log]
  Services --> Idem[Idempotency Records]
```

## Database Design
```mermaid
erDiagram
  users ||--o{ audit_logs : writes
  users ||--o{ idempotency_records : owns
  customers ||--o{ orders : places
  orders ||--o{ order_items : contains
  products ||--o{ order_items : sold_as

  users {
    int id
    string email
    string password_hash
  }
  products {
    int id
    string sku
    decimal unit_price
    int quantity
    datetime deleted_at
  }
  customers {
    int id
    string email
    datetime deleted_at
  }
  orders {
    int id
    string order_number
    decimal total_amount
    string status
    datetime deleted_at
  }
```

## API Design
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/products`, `POST /api/products`, `GET/PATCH/DELETE /api/products/{id}`
- `GET /api/customers`, `POST /api/customers`, `GET/DELETE /api/customers/{id}`
- `GET /api/orders`, `POST /api/orders`, `GET/DELETE /api/orders/{id}`
- `GET /api/dashboard`
- `GET /health`, `GET /health/database`

Errors are normalized:
```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Inventory unavailable"
  }
}
```

## Local Setup
Backend:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/stockroom
alembic -c ..\alembic.ini upgrade head
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Docker Setup
```bash
cp .env.example .env
docker compose up --build
```

Services:
- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`

Compose enables `SEED_DEMO_DATA=true` for the backend, so startup runs migrations and then loads a deterministic demo dataset with an admin user, products, customers, orders, order items, cancellations, and audit logs. The demo login is `admin@stockroomdemo.com` / `Stockroom123!`.

## Testing
```bash
python -m pytest
```

The test suite runs against PostgreSQL, not SQLite. It creates `stockroom_test` on the local Compose Postgres instance when needed, runs Alembic migrations, truncates tables between tests, and covers authentication, product/customer CRUD constraints, order transactions, idempotency conflicts, rollback behavior, cancellation restocking, dashboard metrics, and audit records.

## Deployment
Frontend on Vercel:
- Set `VITE_API_URL` to the Render backend URL.
- Build command: `npm run build`
- Output directory: `dist`

Backend on Render:
- Use the backend Dockerfile from the repository root context.
- Set `DATABASE_URL`, `JWT_SECRET`, and `CORS_ORIGINS`.
- Startup runs `alembic upgrade head` before `uvicorn`.

## Screenshots
Capture these after seeding a production-like environment:
- `screenshots/dashboard.png`
- `screenshots/products.png`
- `screenshots/customers.png`
- `screenshots/orders.png`
- `screenshots/login.png`

## Tradeoffs
- React Router was intentionally avoided; local route state keeps the MVP simple and maintainable.
- PostgreSQL-backed tests require a local database but exercise the same database engine, constraints, and migrations used by the running app.
- The app favors UX polish, validation, and operational correctness over lower-priority extras like exports or advanced reporting.

## Future Improvements
- Add product update forms in the frontend.
- Add automated screenshot capture.
- Add role-based permissions for larger teams.
- Add CSV import/export once the core workflows are deployed.

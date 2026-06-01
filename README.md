# Stockroom

<p align="center">
  <img src="stockroom-logo-text.png" alt="Stockroom logo" width="360" />
</p>

<p align="center">
  A polished inventory and order management MVP for small-business operators.
</p>

<p align="center">
  <strong>React</strong> | <strong>FastAPI</strong> | <strong>PostgreSQL</strong> | <strong>Docker</strong> | <strong>JWT Auth</strong> | <strong>Transactional Orders</strong>
</p>

---

## Overview

Stockroom is a production-minded full-stack inventory system built for day-to-day operational control. It helps teams manage products, customers, and sales orders from a focused SaaS-style dashboard, while the backend enforces the rules that matter: authenticated access, unique SKUs, customer constraints, stock protection, idempotent order creation, audit logs, and PostgreSQL-backed persistence.

The project is intentionally more than a CRUD demo. It includes a branded React interface, a modular FastAPI API, Alembic migrations, Dockerized services, deterministic demo data, and an integration-style pytest suite that exercises the same PostgreSQL behavior used by the app.

## Live Product Experience

Stockroom opens into a branded SaaS workspace with:

- A premium authentication screen with login and registration.
- A command-center dashboard for revenue, orders, customers, inventory value, and stock health.
- Product management with SKU tracking, pricing, stock thresholds, edit flows, and soft deletes.
- Customer management with searchable buyer records.
- Order creation with customer/product selection, multi-line items, live estimated totals, and idempotency keys.
- Order detail inspection and cancellation that automatically returns stock.
- Responsive data tables with search, sorting, pagination, loading states, empty states, and toast feedback.

## Demo Login

When running with the default Docker Compose configuration, demo data is seeded automatically.

```text
Email:    admin@stockroomdemo.com
Password: Stockroom123!
```

## Highlights

| Area | What is included |
| --- | --- |
| Authentication | JWT registration, login, protected frontend routes, authenticated API access |
| Inventory | Product CRUD, unique SKU enforcement, low-stock thresholds, soft deletes |
| Customers | Customer creation, listing, detail lookup, unique email enforcement, soft deletes |
| Orders | Transactional order creation, row locking, stock decrement, order totals, cancellation/restocking |
| Reliability | `Idempotency-Key` support for retry-safe order creation |
| Observability | `X-Request-ID` middleware, structured JSON logging, normalized error envelopes |
| Data | PostgreSQL models, Alembic migrations, deterministic seed data |
| UX | Branded shell, lucide icons, polished tables, modals, skeleton states, empty states, toasts |
| Testing | PostgreSQL-backed pytest suite covering auth, constraints, transactions, idempotency, dashboard metrics |
| Deployment | Dockerfiles for frontend/backend and Compose for local orchestration |

## Tech Stack

### Frontend

- React + Vite
- Plain CSS design system
- Lucide React icons
- Token-based API client
- Local route state for a compact MVP navigation model

### Backend

- FastAPI
- SQLAlchemy ORM
- Pydantic schemas
- Alembic migrations
- PostgreSQL via `psycopg`
- JWT auth with `python-jose`
- Password hashing with Passlib/bcrypt
- Pytest + HTTPX test client

### Infrastructure

- Docker Compose
- PostgreSQL 16 Alpine
- Backend Docker image on Python 3.12 slim
- Frontend production image served by Nginx

## Architecture

```mermaid
flowchart LR
  User[Operator] --> Frontend[React + Vite UI]
  Frontend -->|Bearer JWT REST calls| API[FastAPI API]
  API --> Auth[Auth + Dependencies]
  API --> Services[Business Services]
  Services --> Database[(PostgreSQL)]
  Services --> Audit[Audit Logs]
  API --> Logs[JSON Logs + X-Request-ID]
```

```mermaid
flowchart TB
  Routers[API Routers] --> Schemas[Pydantic Schemas]
  Routers --> Dependencies[JWT User Dependency]
  Routers --> ServiceLayer[Order + Audit Services]
  ServiceLayer --> Models[SQLAlchemy Models]
  Models --> Postgres[(PostgreSQL)]
  Alembic[Alembic Migrations] --> Postgres
  Tests[Pytest Suite] --> Postgres
```

## Data Model

```mermaid
erDiagram
  users ||--o{ audit_logs : writes
  users ||--o{ idempotency_records : owns
  customers ||--o{ orders : places
  orders ||--o{ order_items : contains
  products ||--o{ order_items : sold_as

  users {
    int id
    string name
    string email
    string password_hash
    datetime deleted_at
  }

  products {
    int id
    string name
    string sku
    text description
    decimal unit_price
    int quantity
    int low_stock_threshold
    datetime deleted_at
  }

  customers {
    int id
    string name
    string email
    string company
    string phone
    datetime deleted_at
  }

  orders {
    int id
    string order_number
    int customer_id
    string status
    decimal total_amount
    datetime deleted_at
  }

  order_items {
    int id
    int order_id
    int product_id
    int quantity
    decimal unit_price
    decimal line_total
  }

  idempotency_records {
    int id
    int user_id
    string key
    string request_hash
    text response_body
    int status_code
  }

  audit_logs {
    int id
    string entity_type
    int entity_id
    string action
    int user_id
  }
```

## Repository Map

```text
.
+-- backend/
|   +-- app/
|   |   +-- api/              # FastAPI routers for auth, products, customers, orders, dashboard, health
|   |   +-- auth/             # JWT creation, password hashing, current-user dependency
|   |   +-- core/             # Config, errors, structured logging
|   |   +-- db/               # SQLAlchemy session and base
|   |   +-- middleware/       # Request ID middleware
|   |   +-- models/           # SQLAlchemy entities
|   |   +-- schemas/          # Pydantic request/response models
|   |   +-- scripts/          # Deterministic demo seeding
|   |   +-- services/         # Order transaction and audit services
|   +-- tests/                # PostgreSQL-backed pytest coverage
|   +-- Dockerfile
|   +-- requirements.txt
+-- frontend/
|   +-- public/brand/         # Stockroom brand assets
|   +-- src/
|   |   +-- components/       # Tables, modals, headers, toast, brand components
|   |   +-- features/auth/    # Auth context
|   |   +-- layouts/          # App shell/sidebar
|   |   +-- pages/            # Dashboard, products, customers, orders, auth
|   |   +-- routes/           # App route state
|   |   +-- services/         # API client
|   |   +-- styles/           # Application CSS
|   +-- Dockerfile
|   +-- package.json
+-- alembic/                  # Database migrations
+-- docker-compose.yml        # PostgreSQL + backend + frontend
+-- .env.example              # Local environment template
+-- pytest.ini
```

## API Surface

All protected endpoints require:

```http
Authorization: Bearer <token>
```

### Authentication

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Create a user and return a JWT |
| `POST` | `/api/auth/login` | Exchange credentials for a JWT |
| `GET` | `/api/auth/me` | Return the authenticated user |

### Products

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/products` | List products with search, sort, and pagination |
| `POST` | `/api/products` | Create a product |
| `GET` | `/api/products/{id}` | Get product details |
| `PUT` | `/api/products/{id}` | Replace product fields |
| `PATCH` | `/api/products/{id}` | Partially update a product |
| `DELETE` | `/api/products/{id}` | Soft delete a product |

### Customers

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/customers` | List customers with search, sort, and pagination |
| `POST` | `/api/customers` | Create a customer |
| `GET` | `/api/customers/{id}` | Get customer details |
| `DELETE` | `/api/customers/{id}` | Soft delete a customer |

### Orders

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/orders` | List orders with search, sort, and pagination |
| `POST` | `/api/orders` | Create an order transactionally |
| `GET` | `/api/orders/{id}` | Get order details |
| `DELETE` | `/api/orders/{id}` | Cancel an order and restock inventory |

### Dashboard and Health

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/dashboard` | Return dashboard metrics, recent orders, and stock alerts |
| `GET` | `/health` | App health check |
| `GET` | `/health/database` | Database health check |

The app also exposes assessment-compatible resource aliases without the `/api` prefix:

```text
/products
/customers
/orders
/dashboard
```

## API Behavior Details

### Normalized Errors

Every handled API error follows a consistent envelope.

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Only 3 units available for Relay Barcode Scanner"
  }
}
```

### Retry-Safe Order Creation

Order creation accepts an `Idempotency-Key` header. Repeating the same request with the same key returns the original order response. Reusing the key with a different payload returns an `IDEMPOTENCY_CONFLICT` error.

```http
POST /api/orders
Authorization: Bearer <token>
Idempotency-Key: checkout-123
Content-Type: application/json
```

```json
{
  "customer_id": 1,
  "items": [
    { "product_id": 3, "quantity": 2 }
  ]
}
```

### Transactional Inventory Protection

When an order is created, Stockroom:

1. Validates the customer exists and is active.
2. Locks selected product rows with `FOR UPDATE`.
3. Rejects missing or deleted products.
4. Rejects insufficient stock.
5. Decrements inventory only after validation passes.
6. Calculates server-side totals.
7. Writes an audit log.
8. Stores the idempotency response when a key is provided.

If any step fails, the transaction rolls back and inventory remains unchanged.

## Quick Start With Docker

Docker is the fastest way to run the complete application.

```bash
cp .env.example .env
docker compose up --build
```

Open:

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:8080` |
| Backend API | `http://localhost:8000` |
| OpenAPI Docs | `http://localhost:8000/docs` |
| App Health | `http://localhost:8000/health` |
| Database Health | `http://localhost:8000/health/database` |

The backend container runs Alembic migrations at startup. With `SEED_DEMO_DATA=true`, it also seeds:

- 1 demo admin user
- 40 products
- 40 customers
- 90 orders
- Order items
- Cancelled order examples
- Audit log rows

## Local Development

### 1. Start PostgreSQL

You can use the Compose database service:

```bash
docker compose up postgres
```

### 2. Configure Environment

For local backend development outside Docker, point `DATABASE_URL` at localhost:

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/stockroom"
$env:JWT_SECRET="local-development-secret-change-me"
$env:CORS_ORIGINS="http://localhost:5173,http://localhost:8080"
```

### 3. Run the Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic -c ..\alembic.ini upgrade head
python -m app.scripts.seed_demo
uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`

### 4. Run the Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

If the backend is not running on `http://localhost:8000`, set `VITE_API_URL` before starting Vite.

## Environment Variables

| Variable | Default / Example | Purpose |
| --- | --- | --- |
| `POSTGRES_DB` | `stockroom` | Compose database name |
| `POSTGRES_USER` | `postgres` | Compose database user |
| `POSTGRES_PASSWORD` | `postgres` | Compose database password |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@postgres:5432/stockroom` | Backend database connection |
| `JWT_SECRET` | `replace-with-a-long-random-secret` | JWT signing secret |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080` | Allowed frontend origins |
| `VITE_API_URL` | `http://localhost:8000` | Frontend API base URL |
| `SEED_DEMO_DATA` | `true` | Seed deterministic demo data on backend startup |

## Testing

Run the full test suite from the repository root:

```bash
python -m pytest
```

The tests are intentionally PostgreSQL-backed, not SQLite-backed. They create and migrate a test database, truncate state between tests, and verify behavior against the same database engine used in development and Docker.

Covered areas include:

- Auth registration and login
- Protected API access
- Product and customer uniqueness constraints
- Product update and soft delete behavior
- Assessment-compatible route aliases
- Transactional order creation
- Insufficient-stock rollback
- Idempotency replay and conflict handling
- Order cancellation and inventory restocking
- Dashboard metrics and low-stock alerts
- Audit log creation
- Health endpoints

## Deployment Notes

### Frontend on Vercel

- Project directory: `frontend`
- Install command: `npm install`
- Build command: `npm run build`
- Output directory: `dist`
- Set `VITE_API_URL` to the deployed backend URL.

### Backend on Render

- Use the repository root as the Docker build context.
- Use `backend/Dockerfile`.
- Set `DATABASE_URL`, `JWT_SECRET`, and `CORS_ORIGINS`.
- The Docker command runs `alembic upgrade head` before starting Uvicorn.
- Set `SEED_DEMO_DATA=false` for production-like deployments unless demo data is desired.

## Product Screens To Capture

The app is ready for screenshots after running Docker Compose and logging in with the demo user.

Recommended capture list:

- Dashboard command center
- Products table and product modal
- Customers table and customer modal
- Orders table and order detail modal
- Login/register screen
- Mobile responsive sidebar/auth view

## Assessment Checklist

- [x] React frontend with responsive dashboard, products, customers, and orders views
- [x] FastAPI backend with PostgreSQL persistence
- [x] Product, customer, order, and dashboard APIs
- [x] `/api/*` routes plus assessment-compatible route aliases
- [x] Product create/list/detail/update/delete
- [x] Customer create/list/detail/delete
- [x] Order create/list/detail/cancel
- [x] Unique SKU and customer email constraints
- [x] Inventory validation and insufficient-stock protection
- [x] Automatic stock decrement on order creation
- [x] Stock restoration on order cancellation
- [x] Server-calculated order totals
- [x] JWT authentication
- [x] Idempotent order creation
- [x] Audit logs
- [x] Request IDs and structured logging
- [x] Normalized error responses
- [x] Health checks
- [x] Dockerfiles for backend and frontend
- [x] Docker Compose for frontend, backend, and PostgreSQL
- [x] Deterministic seed data
- [x] PostgreSQL-backed test suite
- [x] Branded UI assets, favicon, and SaaS-style interface polish

## Design Philosophy

Stockroom favors operational correctness and interface clarity over unnecessary breadth. The frontend keeps workflows direct and compact. The backend centralizes business rules where they belong, especially around inventory mutation and order creation. Tests run against PostgreSQL because constraints, transactions, row locks, and migrations are core to the product's reliability.

## Future Enhancements

- Role-based permissions for multi-user teams
- CSV import/export for products and customers
- Advanced reporting by product, customer, and time period
- Audit log viewer in the admin UI
- Product category filtering
- Webhook notifications for low-stock events
- Automated screenshot capture for release checks

---

<p align="center">
  Built as a complete, reviewer-ready full-stack inventory management system.
</p>

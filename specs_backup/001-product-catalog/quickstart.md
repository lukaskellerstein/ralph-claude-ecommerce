# Quickstart: Product Catalog

## Prerequisites

- Docker and Docker Compose installed
- Git
- Node.js 20+ (for frontend development outside Docker)
- Python 3.12+ (for backend development outside Docker)

## Start the Development Stack

```bash
# Clone and enter the project
git clone <repo-url>
cd ralph-claude-ecommerce

# Copy environment configuration
cp .env.example .env
# Edit .env with your settings (database URL, secret key, etc.)

# Start everything
docker compose up
```

This starts:
- **PostgreSQL 16** on port 5432
- **FastAPI backend** on port 8000 (with hot reload)
- **Vite frontend** on port 5173 (with HMR)

## Verify Setup

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/products
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## Run Migrations

```bash
# Run from backend directory (or via Docker)
cd backend
alembic upgrade head
```

## Seed Sample Data

```bash
# Run the seed script to populate categories, products, images, variants, and reviews
cd backend
python -m app.scripts.seed
```

## Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Key API Endpoints for This Feature

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/products | List products (filter, sort, search, paginate) |
| GET | /api/v1/products/{slug} | Product detail |
| GET | /api/v1/products/{slug}/reviews | Product reviews (paginated) |
| POST | /api/v1/products/{slug}/reviews | Submit a review (auth required) |
| PUT | /api/v1/products/{slug}/reviews/{id} | Update own review (auth required) |
| GET | /api/v1/categories | Category tree |

## Key Frontend Pages

| Route | Description |
|-------|-------------|
| /products | Product listing with category nav, filters, sort, search |
| /products?category={slug} | Filtered by category |
| /products?q={query} | Search results |
| /products/{slug} | Product detail page |

## Development Workflow

1. **Backend changes**: Edit files in `backend/app/`. FastAPI auto-reloads.
2. **Frontend changes**: Edit files in `frontend/src/`. Vite HMR applies instantly.
3. **Database schema changes**: Create migration with `alembic revision --autogenerate -m "description"`, then apply with `alembic upgrade head`.
4. **Add a new API endpoint**: Create route in `backend/app/api/v1/`, add Pydantic schemas in `backend/app/schemas/`, add service logic in `backend/app/services/`, write test in `backend/tests/`.
5. **Add a new frontend page**: Create page component in `frontend/src/pages/`, add TanStack Query hook in `frontend/src/hooks/`, write test in `frontend/tests/`.

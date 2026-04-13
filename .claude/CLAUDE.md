# Project

## Governing Principles for Ecommerce Application

### Article 1: Architecture

The application follows a strict frontend/backend separation. The React frontend communicates with the Python backend exclusively through a RESTful JSON API. No server-side rendering. No direct database access from the frontend.

### Article 2: Technology Stack (Non-Negotiable)

- **Frontend**: React 18+ with TypeScript, Vite, shadcn/ui, Tailwind CSS, TanStack Query
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic
- **Database**: PostgreSQL 16+
- **Auth**: JWT with httpOnly cookie transport, bcrypt password hashing
- **Payments**: Stripe Payment Intents API

### Article 3: Code Quality

- All API endpoints MUST have Pydantic request/response schemas.
- All database models MUST use Alembic migrations — no raw SQL schema changes.
- All user-facing inputs MUST be validated on both frontend (zod) and backend (Pydantic).
- TypeScript strict mode is mandatory. No `any` types except in generated code.
- Python code MUST pass `ruff` linting and `mypy` type checks.

### Article 4: Testing Standards

- Every API endpoint MUST have at least one integration test using `pytest` + `httpx`.
- Every React page MUST have at least one component test using Vitest + Testing Library.
- Critical flows (auth, checkout, payment) MUST have end-to-end tests.
- Test database uses a separate PostgreSQL schema, never the production database.

### Article 5: Security

- Passwords are NEVER stored in plaintext — bcrypt only.
- SQL queries MUST use parameterized statements via SQLAlchemy ORM — no raw string interpolation.
- All API endpoints that modify data MUST require authentication unless explicitly public.
- CORS is restricted to known frontend origins.
- Rate limiting is applied to auth endpoints.
- Stripe webhook signatures MUST be verified.

### Article 6: API Design

- RESTful conventions: plural nouns for resources (`/products`, `/orders`).
- Cursor-based pagination for all list endpoints.
- Consistent error response format: `{ "detail": "message", "code": "ERROR_CODE" }`.
- API versioning via URL prefix: `/api/v1/`.
- All monetary values stored as integers (cents) in the database, formatted on the frontend.

### Article 7: Database

- UUIDs for all primary keys.
- `created_at` and `updated_at` timestamps on every table.
- Soft deletes for user-facing data (products, orders). Hard deletes only for ephemeral data (cart items, sessions).
- Foreign key constraints enforced at the database level.
- Indexes on all foreign keys and frequently queried columns.

### Article 8: Performance

- API response time target: < 200ms p95 for read endpoints, < 500ms p95 for writes.
- Frontend Largest Contentful Paint target: < 2.5s.
- Database queries MUST NOT use `SELECT *` — always specify columns.
- Product listing pages MUST support server-side filtering, sorting, and pagination.

### Article 9: Developer Experience

- Single `docker compose up` to start the entire development stack.
- Environment configuration via `.env` files — no hardcoded secrets.
- API documentation auto-generated via FastAPI's OpenAPI spec.
- Frontend and backend can be developed and tested independently.
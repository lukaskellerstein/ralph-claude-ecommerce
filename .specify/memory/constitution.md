<!--
  Sync Impact Report
  ===================
  Version change: (new) → 1.0.0
  Modified principles: N/A (initial population)
  Added sections:
    - 9 Core Principles (Architecture, Technology Stack, Code Quality,
      Testing Standards, Security, API Design, Database, Performance,
      Developer Experience)
    - Operational Standards section
    - Development Workflow section
    - Governance section
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no changes needed
    - .specify/templates/spec-template.md ✅ no changes needed
    - .specify/templates/tasks-template.md ✅ no changes needed
  Follow-up TODOs: None
-->

# Ecommerce Application Constitution

## Core Principles

### I. Architecture

The application follows a strict frontend/backend separation.
The React frontend communicates with the Python backend exclusively
through a RESTful JSON API. No server-side rendering. No direct
database access from the frontend.

- Frontend and backend MUST be deployable independently.
- All communication between frontend and backend MUST use the
  REST JSON API — no shared memory, no direct imports.

### II. Technology Stack (Non-Negotiable)

The following stack is mandatory and MUST NOT be substituted
without a constitutional amendment:

- **Frontend**: React 18+ with TypeScript, Vite, shadcn/ui,
  Tailwind CSS, TanStack Query
- **Backend**: Python 3.12+, FastAPI, Pydantic v2,
  SQLAlchemy 2.0 (async), Alembic
- **Database**: PostgreSQL 16+
- **Auth**: JWT with httpOnly cookie transport, bcrypt password
  hashing
- **Payments**: Stripe Payment Intents API

### III. Code Quality

- All API endpoints MUST have Pydantic request/response schemas.
- All database models MUST use Alembic migrations — no raw SQL
  schema changes.
- All user-facing inputs MUST be validated on both frontend (zod)
  and backend (Pydantic).
- TypeScript strict mode is mandatory. No `any` types except in
  generated code.
- Python code MUST pass `ruff` linting and `mypy` type checks.

### IV. Testing Standards

- Every API endpoint MUST have at least one integration test
  using `pytest` + `httpx`.
- Every React page MUST have at least one component test using
  Vitest + Testing Library.
- Critical flows (auth, checkout, payment) MUST have end-to-end
  tests.
- Test database uses a separate PostgreSQL schema, never the
  production database.

### V. Security

- Passwords are NEVER stored in plaintext — bcrypt only.
- SQL queries MUST use parameterized statements via SQLAlchemy
  ORM — no raw string interpolation.
- All API endpoints that modify data MUST require authentication
  unless explicitly marked as public.
- CORS is restricted to known frontend origins.
- Rate limiting is applied to auth endpoints.
- Stripe webhook signatures MUST be verified.

### VI. API Design

- RESTful conventions: plural nouns for resources
  (`/products`, `/orders`).
- Cursor-based pagination for all list endpoints.
- Consistent error response format:
  `{ "detail": "message", "code": "ERROR_CODE" }`.
- API versioning via URL prefix: `/api/v1/`.
- All monetary values stored as integers (cents) in the database,
  formatted on the frontend.

### VII. Database

- UUIDs for all primary keys.
- `created_at` and `updated_at` timestamps on every table.
- Soft deletes for user-facing data (products, orders). Hard
  deletes only for ephemeral data (cart items, sessions).
- Foreign key constraints enforced at the database level.
- Indexes on all foreign keys and frequently queried columns.

### VIII. Performance

- API response time target: < 200ms p95 for read endpoints,
  < 500ms p95 for writes.
- Frontend Largest Contentful Paint target: < 2.5s.
- Database queries MUST NOT use `SELECT *` — always specify
  columns.
- Product listing pages MUST support server-side filtering,
  sorting, and pagination.

### IX. Developer Experience

- Single `docker compose up` to start the entire development
  stack.
- Environment configuration via `.env` files — no hardcoded
  secrets.
- API documentation auto-generated via FastAPI's OpenAPI spec.
- Frontend and backend can be developed and tested independently.

## Operational Standards

All features and changes MUST comply with the principles above.
Any code that violates a principle MUST be flagged during review
and corrected before merge.

- Principle violations in pull requests are blocking — they MUST
  be resolved before approval.
- Performance targets (Principle VIII) MUST be validated in CI
  for critical paths.
- Security requirements (Principle V) MUST be covered by
  automated checks where feasible (e.g., linting for raw SQL,
  secret scanning).

## Development Workflow

- All changes MUST go through pull request review.
- Feature branches MUST branch from and merge back into `main`.
- Database migrations MUST be reviewed for backward compatibility
  before merge.
- Environment secrets MUST never appear in version control — use
  `.env` files excluded via `.gitignore`.

## Governance

This constitution is the authoritative source of architectural
and quality standards for the ecommerce application. It supersedes
all other documentation when conflicts arise.

- **Amendments**: Any change to this constitution requires
  documentation of the change, rationale, and a version bump
  following semantic versioning.
- **Versioning**: MAJOR for principle removals or incompatible
  redefinitions, MINOR for new principles or material expansions,
  PATCH for clarifications and wording fixes.
- **Compliance**: All pull requests and code reviews MUST verify
  compliance with these principles. Non-compliance MUST be
  documented and justified if temporarily accepted.

**Version**: 1.0.0 | **Ratified**: 2026-04-14 | **Last Amended**: 2026-04-14

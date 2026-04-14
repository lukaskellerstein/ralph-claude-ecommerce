# Implementation Plan: Admin Dashboard

**Branch**: `000-specifications` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-admin-dashboard/spec.md`

## Summary

The Admin Dashboard provides store operators with tools to manage products (CRUD with images and variants), categories (tree hierarchy), orders (status updates, refunds), users (role/status management), and business analytics (revenue, top products, KPIs). It lives under `/admin` routes and is restricted to users with the `admin` role. This feature does not introduce new database tables — it adds admin-facing endpoints and UI over existing entities from Specs 001-004. The implementation uses a FastAPI backend with admin authorization dependency and a React frontend with admin-specific pages, data tables, and chart components.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe, python-multipart, cachetools (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod, recharts, react-md-editor (frontend)
**Storage**: PostgreSQL 16+, local filesystem for product images
**Testing**: pytest + httpx (backend integration tests); Vitest + Testing Library (frontend component tests)
**Target Platform**: Linux server (backend), modern browsers (frontend)
**Project Type**: Web application (frontend SPA + backend API)
**Performance Goals**: < 200ms p95 API reads, < 500ms p95 API writes, < 3s dashboard load, < 2.5s LCP
**Constraints**: Admin role-gated access, image upload max 5MB/10 per product, dashboard cache 5min TTL, no SELECT *, cursor-based pagination
**Scale/Scope**: 1,000+ products, 10,000+ orders, 10,000+ users, 5 admin KPIs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Architecture (frontend/backend separation) | PASS | Admin UI is part of the React SPA. Admin API endpoints are part of the FastAPI backend. Same REST JSON communication pattern. |
| II. Technology Stack | PASS | All mandated technologies used. Added python-multipart (FastAPI file uploads), cachetools (in-memory cache), recharts (charts), react-md-editor (rich text). |
| III. Code Quality | PASS | Pydantic schemas for all admin endpoints. No new DB migrations (existing tables). Zod validation for admin forms. TS strict. ruff + mypy. |
| IV. Testing Standards | PASS | pytest + httpx for all admin API tests. Vitest + Testing Library for all admin pages. |
| V. Security | PASS | Admin role check on all /api/v1/admin/* endpoints. SQLAlchemy ORM. File upload validation (type, size). Last-admin protection. |
| VI. API Design | PASS | RESTful /api/v1/admin/*. Cursor-based pagination. Consistent error format. Cents for monetary values. |
| VII. Database | PASS | No new tables. Uses existing UUIDs, timestamps, soft deletes. FK constraints maintained. |
| VIII. Performance | PASS | Dashboard cache (5min TTL). Server-side pagination for data tables. No SELECT *. |
| IX. Developer Experience | PASS | docker compose up. .env for media config. FastAPI OpenAPI docs. Independent FE/BE dev. |

**Gate result**: ALL PASS — proceeding to Phase 0.

**Post-Phase 1 re-check**: ALL PASS — no new violations introduced during design.

## Project Structure

### Documentation (this feature)

```text
specs/005-admin-dashboard/
├── plan.md                    # This file
├── research.md                # Phase 0 output
├── data-model.md              # Phase 1 output
├── quickstart.md              # Phase 1 output
├── contracts/                 # Phase 1 output
│   ├── admin-products.md      # Product CRUD + images + variants
│   ├── admin-categories.md    # Category CRUD with tree
│   ├── admin-orders.md        # Order management + refunds
│   ├── admin-users.md         # User role/status management
│   └── admin-dashboard.md     # Analytics endpoint
└── tasks.md                   # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── admin/
│   │           ├── __init__.py
│   │           ├── products.py      # Product CRUD, image upload, variant management
│   │           ├── categories.py    # Category CRUD with tree
│   │           ├── orders.py        # Order list, status updates, refunds
│   │           ├── users.py         # User list, role/status changes
│   │           └── dashboard.py     # Analytics stats endpoint
│   ├── core/
│   │   └── admin_deps.py           # require_admin FastAPI dependency
│   ├── schemas/
│   │   └── admin.py                # Admin-specific Pydantic schemas
│   ├── services/
│   │   ├── admin_product_service.py # Product CRUD, slug generation, image management
│   │   ├── admin_category_service.py # Category CRUD, tree validation, deletion protection
│   │   ├── admin_order_service.py   # Order listing (all users), status transitions, refunds
│   │   ├── admin_user_service.py    # User listing, role changes, last-admin protection
│   │   └── dashboard_service.py     # Analytics aggregation with TTL cache
│   └── main.py                     # Mount admin routers, static file serving for media
├── media/                           # Image storage directory (gitignored)
│   └── products/
└── tests/
    ├── test_admin_products.py
    ├── test_admin_categories.py
    ├── test_admin_orders.py
    ├── test_admin_users.py
    └── test_admin_dashboard.py

frontend/
├── src/
│   ├── components/
│   │   └── admin/
│   │       ├── admin-layout.tsx     # Admin sidebar + content layout
│   │       ├── admin-guard.tsx      # Route guard (checks admin role)
│   │       ├── data-table.tsx       # Reusable data table (search, filter, sort, pagination)
│   │       ├── image-upload.tsx     # Image upload with drag-and-drop reorder
│   │       ├── variant-manager.tsx  # Variant add/edit/remove component
│   │       ├── kpi-card.tsx         # KPI summary card component
│   │       ├── revenue-chart.tsx    # Daily revenue chart (recharts)
│   │       └── category-tree.tsx    # Tree view with drag-and-drop ordering
│   ├── pages/
│   │   └── admin/
│   │       ├── dashboard.tsx        # Analytics dashboard (/admin)
│   │       ├── products.tsx         # Product list (/admin/products)
│   │       ├── product-form.tsx     # Create/edit product (/admin/products/new, /admin/products/:id/edit)
│   │       ├── categories.tsx       # Category management (/admin/categories)
│   │       ├── orders.tsx           # Order list (/admin/orders)
│   │       ├── order-detail.tsx     # Admin order detail (/admin/orders/:id)
│   │       └── users.tsx            # User management (/admin/users)
│   ├── hooks/
│   │   ├── use-admin-products.ts    # Admin product API hooks
│   │   ├── use-admin-categories.ts  # Admin category API hooks
│   │   ├── use-admin-orders.ts      # Admin order API hooks
│   │   ├── use-admin-users.ts       # Admin user API hooks
│   │   └── use-admin-dashboard.ts   # Dashboard stats hook
│   ├── lib/
│   │   ├── types.ts                 # Extended with admin-specific types
│   │   └── validations.ts          # Extended with admin form schemas
│   └── App.tsx                     # Add /admin/* routes with admin guard
└── tests/
    └── admin/
        ├── dashboard.test.tsx
        ├── products.test.tsx
        ├── categories.test.tsx
        ├── orders.test.tsx
        └── users.test.tsx
```

**Structure Decision**: Admin endpoints are grouped under `backend/app/api/v1/admin/` as a sub-package to keep them separate from customer-facing endpoints. Each admin domain (products, categories, orders, users, dashboard) has its own service module. Frontend admin pages live under `frontend/src/pages/admin/` and components under `frontend/src/components/admin/`. This keeps the admin UI cleanly separated while sharing the same application shell.

## Complexity Tracking

No constitution violations — this section is not applicable.

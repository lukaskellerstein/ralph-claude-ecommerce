# Implementation Plan: Product Catalog

**Branch**: `000-specifications` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-product-catalog/spec.md`

## Summary

The Product Catalog is the core customer-facing browsable and searchable product interface. It provides category navigation, full-text search, filtering/sorting, product detail pages with image galleries and variant selection, and a review system. The implementation follows a strict frontend/backend separation: a FastAPI backend serving a RESTful JSON API consumed by a React + TypeScript frontend using TanStack Query.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod (frontend)
**Storage**: PostgreSQL 16+ with full-text search (tsvector/tsquery)
**Testing**: pytest + httpx (backend integration tests); Vitest + Testing Library (frontend component tests)
**Target Platform**: Linux server (backend), modern browsers (frontend)
**Project Type**: Web application (frontend SPA + backend API)
**Performance Goals**: < 200ms p95 API reads, < 500ms p95 API writes, < 2.5s LCP frontend
**Constraints**: Cursor-based pagination required, no SELECT *, monetary values in cents, single currency
**Scale/Scope**: 1000+ products, 10,000+ reviews, 50+ categories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Architecture (frontend/backend separation) | PASS | Separate React SPA and FastAPI API communicating via REST JSON |
| II. Technology Stack | PASS | All mandated technologies used: React 18+/TS/Vite/shadcn/Tailwind/TanStack Query (FE), Python 3.12+/FastAPI/Pydantic v2/SQLAlchemy 2.0 async/Alembic (BE), PostgreSQL 16+ |
| III. Code Quality | PASS | Pydantic schemas for all endpoints, Alembic migrations, zod frontend validation, TS strict mode, ruff + mypy |
| IV. Testing Standards | PASS | pytest + httpx for API tests, Vitest + Testing Library for React pages |
| V. Security | PASS | SQLAlchemy ORM (no raw SQL), auth required for write endpoints (review submission), CORS restricted |
| VI. API Design | PASS | RESTful /api/v1/products, /api/v1/categories, cursor-based pagination, consistent error format, cents for monetary values |
| VII. Database | PASS | UUIDs for PKs, created_at/updated_at on all tables, soft deletes for products, FK constraints, indexes on FKs and query columns |
| VIII. Performance | PASS | < 200ms p95 reads, < 2.5s LCP, no SELECT *, server-side filtering/sorting/pagination |
| IX. Developer Experience | PASS | docker compose up, .env config, FastAPI OpenAPI docs, independent FE/BE development |

**Gate result**: ALL PASS — proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-product-catalog/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── products.md
│   ├── categories.md
│   └── reviews.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── products.py       # Product list/detail endpoints
│   │       ├── categories.py     # Category tree endpoint
│   │       └── reviews.py        # Review list/submit endpoints
│   ├── models/
│   │   ├── product.py            # Product, ProductImage, ProductVariant models
│   │   ├── category.py           # Category model
│   │   └── review.py             # Review model
│   ├── schemas/
│   │   ├── product.py            # Pydantic request/response schemas
│   │   ├── category.py
│   │   └── review.py
│   ├── services/
│   │   ├── product_service.py    # Business logic for products
│   │   ├── category_service.py
│   │   └── review_service.py
│   ├── core/
│   │   ├── config.py             # Settings from .env
│   │   ├── database.py           # Async SQLAlchemy engine/session
│   │   ├── deps.py               # Dependency injection (db session, current user)
│   │   └── pagination.py         # Cursor-based pagination utility
│   └── main.py                   # FastAPI app entry point
├── alembic/
│   └── versions/                 # Migration files
├── tests/
│   ├── conftest.py               # Test fixtures (test DB, client, seed data)
│   ├── test_products.py
│   ├── test_categories.py
│   └── test_reviews.py
├── alembic.ini
├── pyproject.toml
├── Dockerfile
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── product-card.tsx      # Product card for listings
│   │   ├── product-gallery.tsx   # Image gallery with thumbnails
│   │   ├── variant-selector.tsx  # Size/color variant picker
│   │   ├── review-list.tsx       # Paginated review display
│   │   ├── review-form.tsx       # Review submission form
│   │   ├── filter-sidebar.tsx    # Price/rating/stock filters
│   │   ├── sort-select.tsx       # Sort dropdown
│   │   ├── category-nav.tsx      # Category navigation sidebar/menu
│   │   ├── search-bar.tsx        # Global search input
│   │   └── rating-display.tsx    # Star rating + distribution bar chart
│   ├── pages/
│   │   ├── product-list.tsx      # Category/search/filtered listing page
│   │   └── product-detail.tsx    # Single product page
│   ├── hooks/
│   │   ├── use-products.ts       # TanStack Query hooks for products API
│   │   ├── use-categories.ts     # TanStack Query hooks for categories API
│   │   └── use-reviews.ts        # TanStack Query hooks for reviews API
│   ├── lib/
│   │   ├── api-client.ts         # Fetch wrapper with base URL, error handling
│   │   ├── types.ts              # Shared TypeScript types
│   │   └── utils.ts              # Format price (cents→display), etc.
│   └── App.tsx
├── tests/
│   ├── product-list.test.tsx
│   └── product-detail.test.tsx
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── package.json
└── Dockerfile

docker-compose.yml                # PostgreSQL + backend + frontend
.env.example                      # Template for environment variables
```

**Structure Decision**: Web application layout with separate `backend/` and `frontend/` directories. This follows Constitution Principle I (strict frontend/backend separation) and Principle IX (independent development and testing). The backend follows a layered architecture: routes → services → models. The frontend follows a feature-oriented structure with shared components.

## Complexity Tracking

No constitution violations — this section is not applicable.

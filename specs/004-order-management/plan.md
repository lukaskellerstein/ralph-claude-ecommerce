# Implementation Plan: Order Management & User Account

**Branch**: `000-specifications` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-order-management/spec.md`

## Summary

Order Management & User Account provides customers with visibility into their order lifecycle (history, detail, status tracking, cancellation with refund), a product wishlist, and a unified account dashboard. This feature extends the Order entity from Spec 003 with status tracking and cancellation, adds a WishlistItem entity, and creates the account hub that ties together profile, addresses, orders, and wishlist. The implementation follows the established frontend/backend separation with a FastAPI backend and React frontend.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod (frontend)
**Storage**: PostgreSQL 16+
**Testing**: pytest + httpx (backend integration tests); Vitest + Testing Library (frontend component tests); e2e tests for cancellation flow
**Target Platform**: Linux server (backend), modern browsers (frontend)
**Project Type**: Web application (frontend SPA + backend API)
**Performance Goals**: < 200ms p95 API reads, < 500ms p95 API writes, < 2.5s LCP frontend
**Constraints**: Order status state machine enforcement, Stripe Refunds API for cancellations, cursor-based pagination, no SELECT *, monetary values in cents
**Scale/Scope**: 10,000+ orders per user (paginated), unlimited wishlist size

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Architecture (frontend/backend separation) | PASS | Separate React SPA and FastAPI API. All order/wishlist/account data via REST JSON API. |
| II. Technology Stack | PASS | All mandated technologies used. Reuses stripe SDK from Spec 003 for refunds. No new non-mandated dependencies. |
| III. Code Quality | PASS | Pydantic schemas for all order/wishlist/account endpoints. Alembic migration for new tables. Zod validation for frontend forms. TS strict. ruff + mypy. |
| IV. Testing Standards | PASS | pytest + httpx for order/wishlist/account API tests. Vitest + Testing Library for all new pages. Cancellation is a critical flow → e2e tests. |
| V. Security | PASS | SQLAlchemy ORM. Auth required for all endpoints. Order access restricted to owner. CORS restricted. Stripe webhook signatures verified (from Spec 003). |
| VI. API Design | PASS | RESTful /api/v1/orders, /api/v1/users/me/wishlist, /api/v1/account. Cursor-based pagination. Consistent error format. Cents for monetary values. |
| VII. Database | PASS | UUIDs for PKs. created_at/updated_at. Soft deletes for orders. Hard deletes for wishlist items (ephemeral). FK constraints. Indexes on FKs and query columns. |
| VIII. Performance | PASS | < 200ms p95 reads. No SELECT *. Paginated queries. Dashboard aggregation is lightweight (single row + counts). |
| IX. Developer Experience | PASS | docker compose up. Same .env as Spec 003. FastAPI OpenAPI docs. Independent FE/BE dev. |

**Gate result**: ALL PASS — proceeding to Phase 0.

**Post-Phase 1 re-check**: ALL PASS — no new violations introduced during design.

## Project Structure

### Documentation (this feature)

```text
specs/004-order-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── orders.md        # Order management endpoints (list, detail, cancel, reorder)
│   ├── wishlist.md      # Wishlist endpoints (list, add, remove, check)
│   └── account.md       # Account dashboard endpoint
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── orders.py            # Order management endpoints (extends Spec 003 checkout.py)
│   │       ├── wishlist.py          # Wishlist endpoints
│   │       └── account.py           # Account dashboard endpoint
│   ├── models/
│   │   ├── order.py                 # Extended with tracking_number, cancelled_at
│   │   ├── order_status.py          # OrderStatusHistory model
│   │   └── wishlist.py              # WishlistItem model
│   ├── schemas/
│   │   ├── order.py                 # Extended with cancel, reorder, status history schemas
│   │   ├── wishlist.py              # Wishlist Pydantic schemas
│   │   └── account.py              # Account dashboard schema
│   ├── services/
│   │   ├── order_service.py         # Order management logic (list, detail, cancel, reorder, status machine)
│   │   ├── wishlist_service.py      # Wishlist business logic
│   │   └── refund_service.py        # Stripe refund operations
│   └── main.py                     # Register new routers
├── alembic/
│   └── versions/
│       └── xxxx_add_order_status_history_wishlist.py
└── tests/
    ├── test_orders.py               # Order management integration tests
    ├── test_wishlist.py             # Wishlist integration tests
    └── test_account.py             # Account dashboard integration tests

frontend/
├── src/
│   ├── components/
│   │   ├── order-status-badge.tsx   # Color-coded status badge component
│   │   ├── order-timeline.tsx       # Status history timeline/stepper
│   │   ├── wishlist-button.tsx      # Heart/bookmark toggle (used on product cards & detail)
│   │   └── account-sidebar.tsx      # Account area navigation sidebar
│   ├── pages/
│   │   ├── account-dashboard.tsx    # Account hub (/account)
│   │   ├── order-history.tsx        # Order list (/account/orders)
│   │   ├── order-detail.tsx         # Order detail (/account/orders/:orderNumber)
│   │   └── wishlist.tsx             # Wishlist page (/account/wishlist)
│   ├── hooks/
│   │   ├── use-orders.ts            # Extended with cancel, reorder mutations
│   │   ├── use-wishlist.ts          # Wishlist query and mutation hooks
│   │   └── use-account.ts           # Dashboard aggregation hook
│   ├── lib/
│   │   ├── types.ts                 # Extended with OrderStatusHistory, WishlistItem, DashboardData types
│   │   └── validations.ts          # Extended with cancel reason schema
│   └── App.tsx                     # Add account area routes
└── tests/
    ├── order-history.test.tsx
    ├── order-detail.test.tsx
    ├── wishlist.test.tsx
    └── account-dashboard.test.tsx
```

**Structure Decision**: Extends the existing web application layout from Specs 001-003. New order management endpoints are in a separate `orders.py` router (distinct from checkout.py in Spec 003) to separate checkout creation from order lifecycle management. The `refund_service.py` isolates Stripe refund operations. The account area uses a shared sidebar layout for consistent navigation.

## Complexity Tracking

No constitution violations — this section is not applicable.

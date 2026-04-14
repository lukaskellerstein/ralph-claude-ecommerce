# Implementation Plan: Shopping Cart & Checkout

**Branch**: `000-specifications` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-shopping-cart-checkout/spec.md`

## Summary

The Shopping Cart & Checkout feature is the revenue-critical path of the ecommerce application. It provides a server-side persistent cart for authenticated users, a localStorage-based guest cart with merge-on-login, and a multi-step checkout flow (shipping address → shipping method → Stripe payment → order confirmation). The implementation follows the established frontend/backend separation: a FastAPI backend with Stripe Payment Intents integration, PostgreSQL with row-level locking for stock management, and a React + TypeScript frontend using Stripe Elements for PCI-compliant payment collection.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod, @stripe/stripe-js, @stripe/react-stripe-js (frontend)
**Storage**: PostgreSQL 16+ with row-level locking (SELECT FOR UPDATE) for stock management
**Testing**: pytest + httpx (backend integration tests); Vitest + Testing Library (frontend component tests); Stripe test mode for payment tests
**Target Platform**: Linux server (backend), modern browsers (frontend)
**Project Type**: Web application (frontend SPA + backend API)
**Performance Goals**: < 200ms p95 API reads, < 500ms p95 API writes, < 2.5s LCP frontend
**Constraints**: Stripe Payment Intents API for payments, card details never touch server, monetary values in cents, cursor-based pagination for order lists, single currency (EUR), flat tax rate
**Scale/Scope**: 10,000+ users, concurrent checkouts for limited stock items, 99.9% webhook processing reliability

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Architecture (frontend/backend separation) | PASS | Separate React SPA and FastAPI API. Cart/checkout state managed via REST API. Guest cart is client-side only until merge. |
| II. Technology Stack | PASS | All mandated technologies used. Added `stripe` Python SDK and `@stripe/stripe-js` + `@stripe/react-stripe-js` as payment-specific dependencies. |
| III. Code Quality | PASS | Pydantic schemas for all cart/checkout/order endpoints. Alembic migrations for CartItem, Order, OrderItem, Payment, OrderCounter tables. Zod validation for checkout forms. TS strict mode. ruff + mypy. |
| IV. Testing Standards | PASS | pytest + httpx for cart/checkout/webhook API tests. Vitest + Testing Library for cart/checkout/confirmation pages. Checkout is a critical flow → e2e tests required. |
| V. Security | PASS | SQLAlchemy ORM (no raw SQL). Auth required for all cart/checkout endpoints. Stripe webhook signatures verified. Card details never touch our server (Stripe Elements). CORS restricted. |
| VI. API Design | PASS | RESTful /api/v1/cart, /api/v1/checkout, /api/v1/orders. Cursor-based pagination for order list. Consistent error format with detail + code. Monetary values in cents. |
| VII. Database | PASS | UUIDs for all PKs. created_at/updated_at on all tables. Soft deletes for orders (user-facing). Hard deletes for cart items (ephemeral). FK constraints. Indexes on FKs and query columns. |
| VIII. Performance | PASS | < 200ms p95 reads, < 500ms p95 writes. No SELECT *. Row-level locking for stock (not table locks). |
| IX. Developer Experience | PASS | docker compose up (Stripe CLI for webhook testing). .env for Stripe keys, tax rate, shipping config. FastAPI OpenAPI docs. Independent FE/BE dev. |

**Gate result**: ALL PASS — proceeding to Phase 0.

**Post-Phase 1 re-check**: ALL PASS — no new violations introduced during design. The data model, API contracts, and project structure all comply with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/003-shopping-cart-checkout/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── cart.md          # Cart endpoints (CRUD + merge)
│   └── checkout.md      # Checkout, orders, Stripe webhook endpoints
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── cart.py              # Cart CRUD + merge endpoints
│   │       ├── checkout.py          # Checkout + order endpoints
│   │       └── webhooks.py          # Stripe webhook handler
│   ├── models/
│   │   ├── cart.py                  # CartItem model
│   │   └── order.py                 # Order, OrderItem, Payment, OrderCounter models
│   ├── schemas/
│   │   ├── cart.py                  # Cart Pydantic request/response schemas
│   │   └── order.py                 # Order/checkout Pydantic schemas
│   ├── services/
│   │   ├── cart_service.py          # Cart business logic (add, update, remove, merge)
│   │   ├── checkout_service.py      # Checkout orchestration, stock validation, order creation
│   │   └── stripe_service.py        # Stripe PaymentIntent creation + webhook processing
│   ├── core/
│   │   └── config.py               # Extended with Stripe keys, tax rate, shipping config
│   └── main.py                     # Add cart, checkout, webhook routers
├── alembic/
│   └── versions/
│       └── xxxx_add_cart_order_tables.py  # Migration: cart_items, orders, order_items, payments, order_counters
└── tests/
    ├── test_cart.py                 # Cart endpoint integration tests
    ├── test_checkout.py             # Checkout flow integration tests
    └── test_webhooks.py             # Stripe webhook integration tests

frontend/
├── src/
│   ├── components/
│   │   ├── cart-item.tsx            # Cart item row (image, name, qty selector, price, remove)
│   │   ├── cart-summary.tsx         # Cart totals sidebar
│   │   ├── checkout-steps.tsx       # Step indicator (address → shipping → payment)
│   │   ├── shipping-address-step.tsx # Step 1: select saved or enter new address
│   │   ├── shipping-method-step.tsx  # Step 2: choose standard/express
│   │   ├── payment-step.tsx         # Step 3: Stripe Elements card input
│   │   └── order-summary-sidebar.tsx # Running total sidebar during checkout
│   ├── pages/
│   │   ├── cart.tsx                 # Cart page (/cart)
│   │   ├── checkout.tsx             # Multi-step checkout page (/checkout)
│   │   └── order-confirmation.tsx   # Confirmation page (/orders/:id/confirmation)
│   ├── hooks/
│   │   ├── use-cart.ts              # TanStack Query hooks for cart API
│   │   ├── use-checkout.ts          # Checkout mutation hooks
│   │   └── use-orders.ts            # Order query hooks
│   ├── lib/
│   │   ├── stripe.ts               # Stripe.js loadStripe initialization
│   │   ├── guest-cart.ts            # localStorage guest cart utilities
│   │   ├── types.ts                 # Extended with cart, order, checkout types
│   │   └── validations.ts          # Extended with checkout form zod schemas
│   └── App.tsx                     # Add cart, checkout, confirmation routes
└── tests/
    ├── cart.test.tsx                # Cart page component tests
    ├── checkout.test.tsx            # Checkout flow component tests
    └── order-confirmation.test.tsx  # Confirmation page component tests
```

**Structure Decision**: Extends the existing web application layout from 001 and 002. New cart/checkout-specific files are added to the established `backend/app/` and `frontend/src/` directories. The `stripe_service.py` module isolates all Stripe API interactions. The checkout service orchestrates the multi-step flow (stock validation → order creation → PaymentIntent creation → stock decrement). No structural changes to existing files beyond extending `config.py`, `main.py`, `types.ts`, `validations.ts`, and `App.tsx`.

## Complexity Tracking

No constitution violations — this section is not applicable.

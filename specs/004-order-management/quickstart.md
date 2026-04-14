# Quickstart: Order Management & User Account

**Feature**: Order Management & User Account
**Date**: 2026-04-14

## Prerequisites

- Specs 001 (Product Catalog), 002 (Auth & User Management), and 003 (Shopping Cart & Checkout) must be implemented.
- Stripe account configured (same as Spec 003 — refund API uses the same secret key).
- PostgreSQL 16+ running (via `docker compose up`).

## Environment Variables

No new environment variables required. This feature uses the existing Stripe configuration from Spec 003.

## Backend Setup

1. Create migration for new/extended tables:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add_order_status_history_and_wishlist"
   alembic upgrade head
   ```

   This migration adds:
   - `order_status_history` table
   - `wishlist_items` table
   - `tracking_number` and `cancelled_at` columns to `orders` table
   - `processing` to order status CHECK constraint

2. New files to create:
   - `backend/app/models/wishlist.py` — WishlistItem model
   - `backend/app/models/order_status.py` — OrderStatusHistory model
   - `backend/app/schemas/wishlist.py` — Wishlist Pydantic schemas
   - `backend/app/schemas/order.py` — Extended with cancel, reorder, status history schemas
   - `backend/app/services/order_service.py` — Order management business logic (list, detail, cancel, reorder, status transitions)
   - `backend/app/services/wishlist_service.py` — Wishlist business logic
   - `backend/app/services/refund_service.py` — Stripe refund operations
   - `backend/app/api/v1/orders.py` — Order management endpoints (extends Spec 003)
   - `backend/app/api/v1/wishlist.py` — Wishlist endpoints
   - `backend/app/api/v1/account.py` — Account dashboard endpoint

3. Register new routers in `backend/app/main.py`.

## Frontend Setup

1. No new npm dependencies required.

2. New files to create:
   - `frontend/src/pages/account-dashboard.tsx` — Account dashboard page
   - `frontend/src/pages/order-history.tsx` — Order history list page
   - `frontend/src/pages/order-detail.tsx` — Order detail page
   - `frontend/src/pages/wishlist.tsx` — Wishlist page
   - `frontend/src/components/order-status-badge.tsx` — Color-coded status badge
   - `frontend/src/components/order-timeline.tsx` — Status timeline/stepper
   - `frontend/src/components/wishlist-button.tsx` — Heart/bookmark toggle
   - `frontend/src/components/account-sidebar.tsx` — Account navigation sidebar
   - `frontend/src/hooks/use-orders.ts` — Extended with cancel, reorder hooks
   - `frontend/src/hooks/use-wishlist.ts` — Wishlist query and mutation hooks
   - `frontend/src/hooks/use-account.ts` — Dashboard data hook

3. Add routes in `frontend/src/App.tsx`:
   - `/account` — Account dashboard (protected)
   - `/account/orders` — Order history (protected)
   - `/account/orders/:orderNumber` — Order detail (protected)
   - `/account/wishlist` — Wishlist (protected)

## Testing

```bash
# Backend
cd backend
pytest tests/test_orders.py tests/test_wishlist.py tests/test_account.py -v

# Frontend
cd frontend
npm test -- --run tests/order-history.test.tsx tests/order-detail.test.tsx tests/wishlist.test.tsx tests/account-dashboard.test.tsx
```

## Stripe Refund Testing

Refunds in test mode work with any previously successful payment:
1. Complete a checkout with test card `4242 4242 4242 4242`.
2. Cancel the order via the cancel endpoint or UI.
3. Verify the refund appears in the Stripe test dashboard under Payments → Refunded.

Note: Stripe test mode refunds are processed instantly. In production, card refunds take 5-10 business days.

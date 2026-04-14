# Quickstart: Shopping Cart & Checkout

**Feature**: Shopping Cart & Checkout
**Date**: 2026-04-14

## Prerequisites

- Specs 001 (Product Catalog) and 002 (Auth & User Management) must be implemented.
- Stripe account with test API keys.
- PostgreSQL 16+ running (via `docker compose up`).

## Environment Variables

Add to `.env`:

```env
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Shipping
FREE_SHIPPING_THRESHOLD=10000
STANDARD_SHIPPING_COST=599
EXPRESS_SHIPPING_COST=1499

# Tax
TAX_RATE=0.21

# Currency
CURRENCY=eur
```

## Backend Setup

1. Install new dependencies:
   ```bash
   pip install stripe
   ```

2. Create migration for cart and order tables:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add_cart_and_order_tables"
   alembic upgrade head
   ```

3. New files to create:
   - `backend/app/models/cart.py` — CartItem model
   - `backend/app/models/order.py` — Order, OrderItem, Payment, OrderCounter models
   - `backend/app/schemas/cart.py` — Cart Pydantic schemas
   - `backend/app/schemas/order.py` — Order/checkout Pydantic schemas
   - `backend/app/services/cart_service.py` — Cart business logic
   - `backend/app/services/checkout_service.py` — Checkout, order creation, stock management
   - `backend/app/services/stripe_service.py` — Stripe PaymentIntent and webhook handling
   - `backend/app/api/v1/cart.py` — Cart endpoints
   - `backend/app/api/v1/checkout.py` — Checkout and order endpoints
   - `backend/app/api/v1/webhooks.py` — Stripe webhook endpoint

4. Register routers in `backend/app/main.py`.

## Frontend Setup

1. Install Stripe.js:
   ```bash
   cd frontend
   npm install @stripe/stripe-js @stripe/react-stripe-js
   ```

2. New files to create:
   - `frontend/src/pages/cart.tsx` — Cart page
   - `frontend/src/pages/checkout.tsx` — Multi-step checkout page
   - `frontend/src/pages/order-confirmation.tsx` — Order confirmation page
   - `frontend/src/components/cart-item.tsx` — Cart item row component
   - `frontend/src/components/cart-summary.tsx` — Cart totals sidebar
   - `frontend/src/components/checkout-steps.tsx` — Step indicator component
   - `frontend/src/components/shipping-address-step.tsx` — Step 1: address
   - `frontend/src/components/shipping-method-step.tsx` — Step 2: shipping
   - `frontend/src/components/payment-step.tsx` — Step 3: Stripe Elements
   - `frontend/src/components/order-summary-sidebar.tsx` — Checkout sidebar
   - `frontend/src/hooks/use-cart.ts` — TanStack Query hooks for cart API
   - `frontend/src/hooks/use-checkout.ts` — Checkout mutation hooks
   - `frontend/src/hooks/use-orders.ts` — Order query hooks
   - `frontend/src/lib/stripe.ts` — Stripe.js initialization
   - `frontend/src/lib/guest-cart.ts` — localStorage guest cart utilities

3. Add routes in `frontend/src/App.tsx`:
   - `/cart` — Cart page
   - `/checkout` — Checkout page (protected route)
   - `/orders/:orderId/confirmation` — Confirmation page (protected route)

## Stripe Test Cards

| Card Number | Scenario |
|-------------|----------|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 0002 | Declined card |
| 4000 0025 0000 3155 | 3D Secure required |

Use any future expiry date, any 3-digit CVC, and any postal code.

## Stripe Webhook Testing (Local)

```bash
# Install Stripe CLI
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
```

The CLI outputs a webhook signing secret — set it as `STRIPE_WEBHOOK_SECRET` in `.env`.

## Testing

```bash
# Backend
cd backend
pytest tests/test_cart.py tests/test_checkout.py tests/test_webhooks.py -v

# Frontend
cd frontend
npm test -- --run tests/cart.test.tsx tests/checkout.test.tsx tests/order-confirmation.test.tsx
```

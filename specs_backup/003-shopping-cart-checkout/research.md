# Research: Shopping Cart & Checkout

**Feature**: Shopping Cart & Checkout
**Date**: 2026-04-14

## R-001: Stripe Payment Intents Integration Pattern

**Decision**: Use Stripe Payment Intents API with server-side PaymentIntent creation and client-side confirmation via Stripe.js / Stripe Elements.

**Rationale**: Payment Intents is Stripe's recommended API for accepting payments. It handles SCA (Strong Customer Authentication) and 3D Secure automatically, is PCI DSS compliant (card details never touch our server), and supports idempotency keys for safe retries. The constitution mandates Stripe Payment Intents API (Principle II).

**Alternatives considered**:
- Stripe Charges API: Deprecated path, no SCA support.
- Stripe Checkout Sessions (hosted): Redirects user away from our site, less control over UX.
- Stripe Payment Links: Too limited for a custom checkout flow.

**Implementation pattern**:
1. Backend creates a PaymentIntent with amount, currency, and metadata (order_id).
2. Backend returns `client_secret` to the frontend.
3. Frontend uses `stripe.confirmCardPayment(clientSecret, { payment_method: { card: element } })`.
4. On success, frontend proceeds to confirmation. Backend also listens for `payment_intent.succeeded` webhook as the authoritative payment confirmation.

---

## R-002: Stock Decrement Race Condition Prevention

**Decision**: Use PostgreSQL `SELECT ... FOR UPDATE` row-level locking within a transaction to atomically check and decrement stock.

**Rationale**: Under concurrent checkouts for limited stock items, naive check-then-decrement allows overselling. Row-level locking ensures only one transaction can read and modify a variant's stock at a time. PostgreSQL's MVCC handles this efficiently without table-level locks.

**Alternatives considered**:
- Optimistic locking with version column: Requires retry logic on conflict, more complex client-side handling.
- Application-level mutex (e.g., Redis lock): Adds infrastructure dependency, less reliable than DB-level guarantees.
- Stored procedure with atomic decrement: Works but moves logic into SQL, harder to test and maintain.

**Implementation pattern**:
```
BEGIN;
SELECT stock_quantity FROM product_variants WHERE id = :variant_id FOR UPDATE;
-- Check stock_quantity >= requested_quantity
UPDATE product_variants SET stock_quantity = stock_quantity - :quantity WHERE id = :variant_id;
-- Create order items
COMMIT;
```

---

## R-003: Guest Cart Merge Strategy

**Decision**: Guest cart stored in localStorage with the same schema as server cart items. On login/register, the frontend sends all guest cart items to a dedicated merge endpoint. Merge uses "higher quantity wins" for duplicates.

**Rationale**: localStorage is the simplest approach for guest persistence — no server-side sessions or anonymous user records needed. The merge endpoint handles conflict resolution server-side, so the logic is centralized and testable.

**Alternatives considered**:
- Server-side anonymous sessions with session cookie: Adds complexity (anonymous user records, session management), requires cleanup jobs.
- IndexedDB: Overkill for simple cart data, less universal browser support.
- Cookie-based cart: Size limits (4KB) make this impractical for carts with multiple items.

**Implementation pattern**:
1. Frontend maintains a `cart` array in localStorage: `[{ product_id, variant_id, quantity }]`.
2. On login/register success, frontend calls `POST /api/v1/cart/merge` with the localStorage cart items.
3. Backend iterates items: for each, if the same product+variant exists in the user's server cart, keep `MAX(server_qty, guest_qty)`. Otherwise, add the item.
4. Frontend clears localStorage cart after successful merge response.

---

## R-004: Stripe Webhook Reliability

**Decision**: Implement webhook handler for `payment_intent.succeeded` and `payment_intent.payment_failed` events. Verify webhook signatures. Use idempotent processing (check if order already updated before applying changes).

**Rationale**: Webhooks are Stripe's recommended way to confirm payment status, as they handle edge cases where the client-side confirmation is lost (network issues, browser close). The constitution mandates webhook signature verification (Principle V).

**Alternatives considered**:
- Client-side confirmation only: Unreliable — user can close browser after payment succeeds but before confirmation callback.
- Polling Stripe API for payment status: Adds latency, wastes API quota, doesn't scale.

**Implementation pattern**:
1. Endpoint: `POST /api/v1/webhooks/stripe` (no auth required, verified by signature).
2. Verify `stripe-signature` header against webhook secret.
3. For `payment_intent.succeeded`: look up order by PaymentIntent ID, update status to `paid`, decrement stock (if not already done).
4. For `payment_intent.payment_failed`: update order status to `payment_failed`.
5. Return 200 immediately — processing is synchronous but fast (single DB transaction).
6. Idempotency: if order is already in `paid` status, skip processing and return 200.

---

## R-005: Order Number Generation

**Decision**: Use a human-readable order number format: `ORD-{YYYYMMDD}-{sequential_counter}`, e.g., `ORD-20260414-00042`. The sequential counter resets daily.

**Rationale**: Order numbers need to be human-readable for customer support, email confirmations, and order tracking. UUIDs are unsuitable for customer-facing identifiers. A date-prefixed sequential format is easy to generate, sortable, and provides instant context about when the order was placed.

**Alternatives considered**:
- UUID only: Not human-friendly, hard to communicate verbally.
- Random alphanumeric (e.g., `A3F9K2`): Risk of collision, no temporal information.
- Global sequential integer: Leaks total order volume, no date context.

**Implementation pattern**:
- Use a PostgreSQL sequence or an `order_counter` table with date-based partitioning.
- Generate within the order creation transaction to ensure uniqueness.
- Store as `order_number VARCHAR(20)` with a unique index.

---

## R-006: Free Shipping Threshold

**Decision**: Standard shipping is free for orders above a configurable threshold (default: 10000 cents / 100 currency units). Express shipping always has its cost applied regardless of order value.

**Rationale**: Free shipping thresholds are a standard ecommerce practice that increases average order value. Making it configurable via environment variable allows adjustment without code changes.

**Alternatives considered**:
- No free shipping in v1: Simpler, but misses a standard conversion optimization.
- Free shipping for all orders: Unrealistic for a real ecommerce application.
- Free shipping on both methods above threshold: Express is a premium service; keeping its cost maintains the value distinction.

---

## R-007: Tax Calculation in v1

**Decision**: Apply a flat tax rate (configurable, default 21%) to the order subtotal. Tax is calculated server-side during checkout and displayed in the order summary.

**Rationale**: Real tax calculation services (Avalara, TaxJar) are explicitly out of scope for v1. A flat rate is the simplest approach that still exercises the tax display and calculation logic in the UI and backend, making it easy to swap in a real service later.

**Implementation pattern**:
- Tax rate stored as an environment variable: `TAX_RATE=0.21`.
- Tax amount = `round(subtotal * tax_rate)` (computed in cents).
- Tax is computed server-side during order creation and stored on the order record.

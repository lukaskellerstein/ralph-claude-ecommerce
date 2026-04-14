# Research: Order Management & User Account

**Feature**: Order Management & User Account
**Date**: 2026-04-14

## R-001: Stripe Refund Integration Pattern

**Decision**: Use the Stripe Refunds API to initiate full refunds on order cancellation. Refund is created server-side using the PaymentIntent ID stored on the Payment record.

**Rationale**: Stripe's Refund API is the standard way to return funds. Full refunds are straightforward — one API call with the PaymentIntent ID. The refund status is confirmed via webhook (`charge.refunded`), but for v1 we treat the API response as sufficient since Stripe processes refunds synchronously for card payments. The constitution mandates Stripe (Principle II).

**Alternatives considered**:
- Manual refund via Stripe Dashboard: Not programmatic, doesn't update order status automatically.
- Partial refund support: Out of scope for v1 per spec assumptions. Full refund only.
- Refund via PaymentIntent cancellation: Only works for uncaptured payments, not applicable here (payments are captured at checkout).

**Implementation pattern**:
1. Validate order status is "paid" or "processing".
2. Call `stripe.Refund.create(payment_intent=pi_id)` to initiate full refund.
3. On success: update order status to "cancelled", payment status to "refunded", restore stock, log status change.
4. On failure: keep order in current status, log the error, return error to user for admin follow-up.

---

## R-002: Order Status Transition Machine

**Decision**: Enforce a strict state machine for order status transitions at the service layer. Valid transitions are defined as a dictionary/map and checked before any status update.

**Rationale**: The spec defines explicit valid transitions (pending → paid → processing → shipped → delivered, or pending/paid/processing → cancelled). Enforcing this at the service layer prevents invalid states and makes the system behavior predictable. An OrderStatusHistory table logs every transition.

**Alternatives considered**:
- Database-level CHECK constraint with trigger: Complex to maintain, harder to provide meaningful error messages.
- No enforcement (trust callers): Risky — admin or webhook bugs could create invalid states.
- State machine library (e.g., python-statemachine): Adds dependency for a simple set of transitions.

**Implementation pattern**:
```
VALID_TRANSITIONS = {
    "pending": ["paid", "cancelled"],
    "paid": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": [],
}
```
Before any status update: check `new_status in VALID_TRANSITIONS[current_status]`. If invalid, raise an error.

---

## R-003: Reorder Strategy

**Decision**: The "reorder" action reads all OrderItems from the specified order and calls the existing cart add-item logic for each. Items that are unavailable (out of stock, soft-deleted, or inactive) are collected and returned as warnings — the available items are still added.

**Rationale**: Reusing the existing cart service for adding items ensures consistency (stock validation, duplicate handling, price lookup). Current prices are used, not historical prices, which matches user expectations when re-purchasing.

**Alternatives considered**:
- Batch add endpoint: Would require a new cart API. The existing add-item endpoint handles upserts correctly, so sequential calls (within a single service method) are sufficient.
- Copy historical prices: Misleading — prices may have changed. Using current prices is the standard ecommerce practice.

**Implementation pattern**:
1. Fetch order items for the given order (verify ownership).
2. For each OrderItem: attempt to add to cart via cart_service.add_item(product_id, variant_id, quantity).
3. Collect successes and failures (with reasons: out of stock, product deleted, variant unavailable).
4. Return: items added to cart + list of unavailable items with reasons.

---

## R-004: Wishlist Data Model

**Decision**: Simple join table (WishlistItem) linking user_id and product_id with a unique constraint. No variant association — wishlist operates at the product level.

**Rationale**: The spec explicitly states wishlist is at the product level, not variant level. A simple join table with a unique constraint prevents duplicates at the database level. No soft delete needed — wishlist items are ephemeral data (hard delete per Constitution Principle VII).

**Alternatives considered**:
- Wishlist as a named list (multiple wishlists per user): Overcomplicated for v1. Single implicit wishlist per user.
- Variant-level wishlist: Spec explicitly scopes to product level.
- Wishlist stored in localStorage (like guest cart): Loses data across devices, doesn't align with the server-side pattern established for authenticated features.

---

## R-005: Account Dashboard Aggregation

**Decision**: The account dashboard fetches summary data from multiple existing endpoints/services and aggregates them into a single response. This avoids creating a separate "dashboard" table — the data is always derived from current state.

**Rationale**: Dashboard data is inherently derived: last order, address count, wishlist count, profile completeness. Caching is unnecessary for v1 at this scale. A single aggregation endpoint keeps the frontend simple (one API call for the dashboard).

**Alternatives considered**:
- Multiple frontend API calls: More round-trips, harder to handle loading states. Better as a single aggregated endpoint.
- Denormalized dashboard table: Adds write complexity to keep in sync, unnecessary at current scale.

**Implementation pattern**:
- Single endpoint: `GET /api/v1/account/dashboard`
- Returns: `{ recent_order: {...} | null, address_count: number, wishlist_count: number, profile_complete: boolean }`
- Backend queries: last order (ORDER BY created_at DESC LIMIT 1), COUNT addresses, COUNT wishlist items, check user.phone is not null.

---

## R-006: Stock Restoration on Cancellation

**Decision**: When an order is cancelled, iterate over all OrderItems and atomically increment the stock_quantity of each referenced ProductVariant using `UPDATE ... SET stock_quantity = stock_quantity + :quantity`.

**Rationale**: This is the inverse of the stock decrement in checkout (Spec 003 R-002). Using atomic increments ensures correctness under concurrency. No row-level locking needed for increments (unlike decrements which must check for negative stock).

**Implementation pattern**:
1. Within the cancellation transaction: for each OrderItem, `UPDATE product_variants SET stock_quantity = stock_quantity + :qty WHERE id = :variant_id`.
2. This runs after the refund succeeds but within the same DB transaction as the status update.
3. If the product has been soft-deleted, stock is still restored (the product may be reactivated).

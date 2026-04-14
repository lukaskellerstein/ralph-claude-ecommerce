# Data Model: Order Management & User Account

**Feature**: Order Management & User Account
**Date**: 2026-04-14

## Entity Relationship Overview

```
Order (from 003-shopping-cart-checkout, extended)
  ├── OrderItem (one-to-many, from 003)
  ├── Payment (one-to-one, from 003)
  └── OrderStatusHistory (one-to-many, NEW)

User (from 002-auth-user-management)
  └── WishlistItem (one-to-many, NEW)
        └── Product (FK, from 001-product-catalog)
```

## Entities

### Order (Extended)

The Order entity from Spec 003 is extended with the following additional fields:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| tracking_number | VARCHAR(100) | NULLABLE | Shipping tracking number (plain text, entered by admin) |
| cancelled_at | TIMESTAMP | NULLABLE | When the order was cancelled (NULL = not cancelled) |

**New indexes**: `tracking_number` (when not null)

All other Order fields remain as defined in Spec 003 data model.

**Extended status CHECK constraint**: `status IN ('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled')`

Note: Spec 003 defined statuses pending, paid, shipped, delivered, cancelled. This spec adds `processing` as an intermediate state between paid and shipped.

---

### OrderStatusHistory (NEW)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| order_id | UUID | FK → Order(id), NOT NULL, ON DELETE CASCADE | Order this status change belongs to |
| previous_status | VARCHAR(20) | NULLABLE | Status before change (NULL for initial creation) |
| new_status | VARCHAR(20) | NOT NULL | Status after change |
| actor_type | VARCHAR(20) | NOT NULL | Who triggered the change: 'system', 'customer', 'admin' |
| actor_id | UUID | NULLABLE | User ID if actor is customer or admin (NULL for system) |
| note | TEXT | NULLABLE | Optional note (e.g., cancellation reason) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the transition occurred |

**Indexes**: `order_id`, `(order_id, created_at)`, `new_status`
**Delete behavior**: CASCADE with parent Order.
**Constraints**: `actor_type` CHECK: `actor_type IN ('system', 'customer', 'admin')`. `new_status` must be a valid order status.

---

### WishlistItem (NEW)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User(id), NOT NULL, ON DELETE CASCADE | Wishlist owner |
| product_id | UUID | FK → Product(id), NOT NULL | Wishlisted product |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the item was added |

**Indexes**: `user_id`, `product_id`, `(user_id, product_id)` (unique)
**Delete behavior**: Hard delete (wishlist items are ephemeral data per Constitution Principle VII).
**Constraints**: Unique constraint on `(user_id, product_id)` prevents duplicate entries.

---

## State Transitions

### Order Status Lifecycle (Complete)

```
pending (order created, awaiting payment)
  → paid (payment confirmed)
  → cancelled (payment failed or customer/admin cancellation)

paid (payment confirmed)
  → processing (admin begins fulfillment)
  → cancelled (customer or admin cancellation, refund initiated)

processing (being fulfilled)
  → shipped (admin marks as shipped, tracking number added)
  → cancelled (admin cancellation, refund initiated)

shipped (in transit)
  → delivered (admin confirms delivery)

delivered (received by customer)
  [terminal state — no further transitions]

cancelled (order cancelled, refund initiated)
  [terminal state — no further transitions]
```

**Cancellation rules**:
- Customer can cancel: `paid`, `processing`
- Admin can cancel: `pending`, `paid`, `processing`
- System can cancel: `pending` (payment failure)
- Cancellation from `paid` or `processing` triggers refund + stock restoration

### Order Status Color Mapping

| Status | Color | Badge |
|--------|-------|-------|
| pending | Yellow | Pending |
| paid | Blue | Paid |
| processing | Blue | Processing |
| shipped | Purple | Shipped |
| delivered | Green | Delivered |
| cancelled | Red | Cancelled |
| refunded | Gray | Refunded |

Note: `refunded` is a payment_status, not an order status. It is displayed when payment_status is "refunded" regardless of order status.

---

## Validation Rules

| Entity | Rule |
|--------|------|
| Order | `tracking_number` if set must be 1-100 characters |
| Order | Status transitions must follow the defined state machine |
| OrderStatusHistory | `actor_type` must be one of: 'system', 'customer', 'admin' |
| OrderStatusHistory | `new_status` must be a valid order status |
| OrderStatusHistory | If `actor_type` is 'customer' or 'admin', `actor_id` must be a valid user UUID |
| WishlistItem | Unique per `(user_id, product_id)` — no duplicate wishlisting |
| WishlistItem | `product_id` must reference an existing product |

## Cross-Feature References

- **Order, OrderItem, Payment** (from 003-shopping-cart-checkout): Extended, not replaced. All existing fields and relationships remain.
- **User** (from 002-auth-user-management): `WishlistItem.user_id` and `OrderStatusHistory.actor_id` FK → `User(id)`.
- **Product** (from 001-product-catalog): `WishlistItem.product_id` FK → `Product(id)`.
- **ProductVariant** (from 001-product-catalog): Stock restoration on cancellation increments `ProductVariant.stock_quantity`.
- **CartItem** (from 003-shopping-cart-checkout): Reorder action uses `cart_service.add_item` to add items to the current cart.

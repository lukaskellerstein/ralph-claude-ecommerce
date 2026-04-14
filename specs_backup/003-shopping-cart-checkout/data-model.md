# Data Model: Shopping Cart & Checkout

**Feature**: Shopping Cart & Checkout
**Date**: 2026-04-14

## Entity Relationship Overview

```
User (from 002-auth-user-management)
  ├── CartItem (one-to-many, ephemeral)
  │     ├── Product (FK, from 001-product-catalog)
  │     └── ProductVariant (FK, optional, from 001-product-catalog)
  └── Order (one-to-many, soft-deleted)
        ├── OrderItem (one-to-many, immutable snapshots)
        └── Payment (one-to-one)

Address (from 002-auth-user-management)
  └── Order.shipping_address_snapshot (JSON copy at time of order)
```

## Entities

### CartItem

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User(id), NOT NULL, ON DELETE CASCADE | Cart owner |
| product_id | UUID | FK → Product(id), NOT NULL | Product in cart |
| variant_id | UUID | FK → ProductVariant(id), NULLABLE | Selected variant (NULL if product has no variants) |
| quantity | INTEGER | NOT NULL, CHECK (quantity > 0) | Desired quantity |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When item was added |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last quantity change |

**Indexes**: `user_id`, `(user_id, product_id, variant_id)` (unique)
**Delete behavior**: Hard delete. Cart items are ephemeral data (Constitution Principle VII). Deleted when removed by user or when order is placed.
**Constraints**: Unique constraint on `(user_id, product_id, variant_id)` prevents duplicate cart entries. `variant_id` uses `COALESCE(variant_id, '00000000-0000-0000-0000-000000000000')` in the unique index to handle NULL variants.

---

### Order

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| order_number | VARCHAR(20) | NOT NULL, UNIQUE | Human-readable number (e.g., ORD-20260414-00042) |
| user_id | UUID | FK → User(id), NOT NULL | Customer who placed the order |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Order status |
| payment_status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Payment status |
| shipping_address | JSONB | NOT NULL | Snapshot of shipping address at time of order |
| shipping_method | VARCHAR(20) | NOT NULL | Selected shipping method ('standard' or 'express') |
| shipping_cost | INTEGER | NOT NULL | Shipping cost in cents |
| subtotal | INTEGER | NOT NULL | Sum of line item totals in cents |
| tax_amount | INTEGER | NOT NULL | Calculated tax in cents |
| total | INTEGER | NOT NULL | Grand total in cents (subtotal + shipping + tax) |
| estimated_delivery_date | DATE | NULLABLE | Estimated delivery based on shipping method |
| deleted_at | TIMESTAMP | NULLABLE | Soft delete timestamp (NULL = active) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Order placement timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last status change |

**Indexes**: `order_number` (unique), `user_id`, `status`, `created_at`, `deleted_at`
**Soft delete**: Orders use soft deletes (Constitution Principle VII — user-facing data).
**Constraints**: `status` CHECK: `status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')`. `payment_status` CHECK: `payment_status IN ('pending', 'succeeded', 'failed')`.

**shipping_address JSONB structure**:
```json
{
  "label": "string",
  "street_line_1": "string",
  "street_line_2": "string | null",
  "city": "string",
  "state": "string",
  "postal_code": "string",
  "country": "string"
}
```

---

### OrderItem

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| order_id | UUID | FK → Order(id), NOT NULL, ON DELETE CASCADE | Parent order |
| product_id | UUID | FK → Product(id), NOT NULL | Original product reference |
| variant_id | UUID | FK → ProductVariant(id), NULLABLE | Original variant reference |
| product_name | VARCHAR(255) | NOT NULL | Snapshot of product name at purchase time |
| variant_type | VARCHAR(50) | NULLABLE | Snapshot of variant type (e.g., "Size") |
| variant_value | VARCHAR(100) | NULLABLE | Snapshot of variant value (e.g., "Large") |
| sku | VARCHAR(100) | NULLABLE | Snapshot of SKU at purchase time |
| unit_price | INTEGER | NOT NULL | Price per unit in cents at purchase time |
| quantity | INTEGER | NOT NULL, CHECK (quantity > 0) | Quantity purchased |
| line_total | INTEGER | NOT NULL | unit_price * quantity in cents |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `order_id`, `product_id`
**Constraints**: `line_total` must equal `unit_price * quantity` (enforced at application level). OrderItems are immutable after creation — they are historical snapshots.

---

### Payment

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| order_id | UUID | FK → Order(id), NOT NULL, UNIQUE | Associated order (one payment per order) |
| stripe_payment_intent_id | VARCHAR(255) | NOT NULL, UNIQUE | Stripe PaymentIntent ID |
| amount | INTEGER | NOT NULL | Payment amount in cents |
| currency | VARCHAR(3) | NOT NULL, DEFAULT 'eur' | ISO 4217 currency code |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Payment status from Stripe |
| stripe_client_secret | VARCHAR(255) | NOT NULL | Client secret for frontend confirmation |
| paid_at | TIMESTAMP | NULLABLE | When payment was confirmed |
| failed_at | TIMESTAMP | NULLABLE | When payment failed (if applicable) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `order_id` (unique), `stripe_payment_intent_id` (unique), `status`
**Constraints**: `status` CHECK: `status IN ('pending', 'succeeded', 'failed', 'cancelled')`. One-to-one relationship with Order via unique constraint on `order_id`.

---

### OrderCounter

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| date | DATE | PK | The date for this counter |
| counter | INTEGER | NOT NULL, DEFAULT 0 | Sequential counter for the day |

**Purpose**: Generates human-readable order numbers. Incremented atomically within the order creation transaction using `UPDATE ... RETURNING` with `INSERT ON CONFLICT`.

---

## State Transitions

### Order Lifecycle

```
pending (created, awaiting payment)
  → paid (payment confirmed via Stripe webhook or client confirmation)
  → cancelled (payment failed or admin cancellation)

paid
  → shipped (admin marks as shipped — future feature)
  → delivered (admin marks as delivered — future feature)
  → cancelled (admin cancellation with refund — future feature)
```

For v1, the primary transitions are:
- `pending` → `paid` (on successful payment)
- `pending` → `cancelled` (on payment failure or timeout)

### Payment Lifecycle

```
pending (PaymentIntent created)
  → succeeded (payment_intent.succeeded webhook)
  → failed (payment_intent.payment_failed webhook)
  → cancelled (PaymentIntent cancelled/expired)
```

### CartItem Lifecycle

```
Active (exists in cart_items table)
  → Updated (quantity changed)
  → Removed (hard deleted by user or on order placement)
```

## Validation Rules

| Entity | Rule |
|--------|------|
| CartItem | `quantity` must be > 0 |
| CartItem | `quantity` must not exceed `stock_quantity` of the referenced variant (or product) |
| CartItem | Unique per `(user_id, product_id, variant_id)` — duplicates increment quantity |
| Order | `subtotal` must equal sum of all OrderItem `line_total` values |
| Order | `total` must equal `subtotal + shipping_cost + tax_amount` |
| Order | `shipping_address` must contain all required address fields |
| Order | `shipping_method` must be one of: 'standard', 'express' |
| OrderItem | `unit_price` must be > 0 |
| OrderItem | `quantity` must be > 0 |
| OrderItem | `line_total` must equal `unit_price * quantity` |
| Payment | `amount` must equal the associated Order's `total` |
| Payment | `stripe_payment_intent_id` must be unique |

## Cross-Feature References

- **User** (from 002-auth-user-management): `CartItem.user_id` and `Order.user_id` FK → `User(id)`.
- **Address** (from 002-auth-user-management): Order stores a JSONB snapshot of the selected address (not a FK, since addresses can be edited/deleted after order placement).
- **Product** (from 001-product-catalog): `CartItem.product_id` and `OrderItem.product_id` FK → `Product(id)`.
- **ProductVariant** (from 001-product-catalog): `CartItem.variant_id` and `OrderItem.variant_id` FK → `ProductVariant(id)`. `stock_quantity` is decremented on order placement.

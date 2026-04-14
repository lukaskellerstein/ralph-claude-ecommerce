# Data Model: Product Catalog

**Feature**: Product Catalog
**Date**: 2026-04-14

## Entity Relationship Overview

```
Category (self-referencing via parent_id)
  └── Product (belongs to one category)
        ├── ProductImage (one-to-many, ordered by position)
        ├── ProductVariant (one-to-many, each with own price/stock)
        └── Review (one-to-many, one per user per product)
                └── User (FK, from auth system)
```

## Entities

### Category

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Display name |
| slug | VARCHAR(100) | NOT NULL, UNIQUE | URL-friendly identifier |
| parent_id | UUID | FK → Category(id), NULLABLE | Parent category (NULL = root) |
| position | INTEGER | NOT NULL, DEFAULT 0 | Display ordering within same level |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `slug` (unique), `parent_id`
**Constraints**: A category with a non-null `parent_id` cannot itself be referenced as a `parent_id` by another category (enforced at application level — max 2 levels).

**Derived field** (computed at query time):
- `product_count`: Number of active products in this category.

---

### Product

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Product display name |
| slug | VARCHAR(255) | NOT NULL, UNIQUE | URL-friendly identifier |
| description | TEXT | NOT NULL | Rich text/markdown description |
| base_price | INTEGER | NOT NULL | Base price in cents |
| category_id | UUID | FK → Category(id), NOT NULL | Owning category |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether product is visible |
| search_vector | TSVECTOR | — | Full-text search index (auto-maintained by trigger) |
| deleted_at | TIMESTAMP | NULLABLE | Soft delete timestamp (NULL = active) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `slug` (unique), `category_id`, `base_price`, `created_at`, `search_vector` (GIN), `is_active`, `deleted_at`
**Soft delete**: Queries filter `WHERE deleted_at IS NULL` by default.

**Derived fields** (computed at query time or via denormalization):
- `average_rating`: Average star rating from reviews.
- `review_count`: Number of reviews.
- `order_count`: Number of times ordered (for "popular" sorting, sourced from orders system).

---

### ProductImage

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| product_id | UUID | FK → Product(id), NOT NULL, ON DELETE CASCADE | Owning product |
| url | VARCHAR(500) | NOT NULL | Image URL (CDN or local) |
| alt_text | VARCHAR(255) | NOT NULL, DEFAULT '' | Accessibility alt text |
| position | INTEGER | NOT NULL, DEFAULT 0 | Display ordering (0 = primary) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `product_id`, `(product_id, position)`

---

### ProductVariant

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| product_id | UUID | FK → Product(id), NOT NULL, ON DELETE CASCADE | Owning product |
| variant_type | VARCHAR(50) | NOT NULL | Type of variant (e.g., "Size", "Color") |
| variant_value | VARCHAR(100) | NOT NULL | Value (e.g., "Large", "Red") |
| sku | VARCHAR(100) | NOT NULL, UNIQUE | Stock keeping unit code |
| price_override | INTEGER | NULLABLE | Override price in cents (NULL = use base_price) |
| stock_quantity | INTEGER | NOT NULL, DEFAULT 0 | Available stock |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `product_id`, `sku` (unique), `(product_id, variant_type, variant_value)` (unique)

---

### Review

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| product_id | UUID | FK → Product(id), NOT NULL | Reviewed product |
| user_id | UUID | FK → User(id), NOT NULL | Reviewing user |
| rating | SMALLINT | NOT NULL, CHECK (1 <= rating <= 5) | Star rating |
| text | TEXT | NOT NULL | Review body text |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `product_id`, `user_id`, `(user_id, product_id)` (unique), `created_at`
**Constraints**: One review per user per product (unique constraint on `user_id, product_id`).

---

## State Transitions

### Product Lifecycle

```
Active (is_active=true, deleted_at=NULL)
  → Deactivated (is_active=false, deleted_at=NULL)   [admin hides product]
  → Soft Deleted (deleted_at=timestamp)               [admin removes product]
```

- Active products are visible in catalog, search, and category listings.
- Deactivated products are hidden from customers but still accessible via direct URL for order history references.
- Soft-deleted products are excluded from all customer queries.

### Variant Stock

```
In Stock (stock_quantity > 0)
  → Out of Stock (stock_quantity = 0)   [decremented by order placement]
```

- Out-of-stock variants are still displayed but marked as unavailable and cannot be added to cart.

## Validation Rules

| Entity | Rule |
|--------|------|
| Product | `base_price` must be > 0 |
| Product | `slug` must be lowercase alphanumeric + hyphens, unique |
| Product | `name` must be 1-255 characters |
| Category | Max 2 levels of nesting (root → child, no grandchild categories) |
| Category | `slug` must be lowercase alphanumeric + hyphens, unique |
| ProductVariant | `stock_quantity` must be >= 0 |
| ProductVariant | `price_override` if set must be > 0 |
| ProductVariant | `sku` must be unique across all variants |
| Review | `rating` must be 1-5 |
| Review | `text` must be 1-5000 characters |
| Review | One review per (user_id, product_id) |
| ProductImage | `position` must be >= 0 |

# Data Model: Admin Dashboard

**Feature**: Admin Dashboard
**Date**: 2026-04-14

## Entity Relationship Overview

```
This feature does not introduce new persistent entities.
It extends admin management capabilities over existing entities:

Product, ProductImage, ProductVariant (from 001) — admin CRUD
Category (from 001) — admin CRUD with tree management
Order, OrderItem, Payment (from 003) — admin status management
OrderStatusHistory (from 004) — admin-triggered entries
User (from 002) — admin role/status management
WishlistItem (from 004) — no admin management

DashboardStats — computed/cached, NOT a persistent entity
```

## Entities

### No New Persistent Entities

All data is managed through existing entities from prior specs. This feature adds admin-facing endpoints and business logic but does not create new database tables.

### DashboardStats (Computed, Not Persisted)

This is a cached computation, not a database table.

| Field | Type | Description |
|-------|------|-------------|
| period_days | integer | Time range: 7, 30, or 90 days |
| total_revenue | integer | Sum of Order.total (in cents) for paid orders in the period |
| total_orders | integer | Count of orders with payment_status='succeeded' in the period |
| average_order_value | integer | total_revenue / total_orders (in cents), 0 if no orders |
| total_customers | integer | Count of all users with role='customer' |
| daily_revenue | array | Array of {date, revenue} objects for each day in the period |
| top_products | array | Top 5 products by order count in the period, each with {product_id, name, order_count, revenue} |
| recent_orders | array | 5 most recent orders with {order_number, customer_name, total, status, created_at} |
| computed_at | timestamp | When this cache entry was computed |

**Cache TTL**: 5 minutes. Cache key: `dashboard_stats_{period_days}`.

---

## Extensions to Existing Entities

### Product (from Spec 001)

No schema changes. Admin endpoints provide full CRUD:
- Create: all fields (name, slug, description, category_id, base_price, is_active)
- Update: all fields
- Deactivate: set is_active = false (soft disable)

### ProductImage (from Spec 001)

No schema changes. Admin endpoints add:
- Upload: multipart file upload with validation (type, size)
- Reorder: update position field
- Delete: hard delete (remove file from filesystem + database record)

### Category (from Spec 001)

No schema changes. Admin endpoints add:
- Create: name, slug, parent_id, position
- Update: name, slug, parent_id, position
- Delete: only if no products AND no subcategories are assigned
- Reorder: update position field for display ordering

### Order (from Specs 003/004)

No schema changes beyond what Spec 004 already added. Admin endpoints provide:
- List all orders (across all users, not just the requesting user)
- Update status with state machine validation
- Add tracking number on ship transition
- Initiate refund

### User (from Spec 002)

No schema changes. Admin endpoints provide:
- List all users with order counts
- Update role (customer ↔ admin) with last-admin protection
- Activate/deactivate with last-admin protection

---

## Validation Rules (Admin-Specific)

| Context | Rule |
|---------|------|
| Product creation | Name must be 1-255 characters |
| Product creation | Slug auto-generated from name, must be unique, editable |
| Product creation | Base price must be > 0 (in cents) |
| Product creation | Category must exist |
| Image upload | Maximum 10 images per product |
| Image upload | Maximum 5MB per image file |
| Image upload | Accepted formats: JPEG, PNG, WebP |
| Variant management | SKU must be unique across all variants |
| Variant management | Stock quantity must be >= 0 |
| Category deletion | Blocked if category has products assigned |
| Category deletion | Blocked if category has subcategories |
| Category nesting | Maximum 2 levels (root → child, no grandchild) |
| Order status change | Must follow valid transition state machine (from Spec 004) |
| Order ship transition | Tracking number is required |
| User role change | Cannot demote/deactivate the last remaining admin |
| User management | Cannot edit name, email, or password — only role and is_active |

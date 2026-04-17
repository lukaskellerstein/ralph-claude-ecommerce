# Eshopy — Product Domain Specification

This document captures the complete product-level requirements for Eshopy v1, derived from the original GOAL.md and subsequent clarification.

---

## 1. User Personas & Roles

### Customer (Shopper)
- **Who**: End users who browse, purchase, and review products.
- **Goals**: Find products quickly, complete purchases smoothly, manage their account and order history.
- **Access**: Public storefront, account area at `/account`.

### Guest Visitor
- **Who**: Unauthenticated users browsing the store.
- **Goals**: Browse products, build a cart, and decide whether to register.
- **Access**: Public storefront only. Must log in or register to check out, leave reviews, or access account features.
- **Cart behavior**: Guest cart is stored in the browser (localStorage). On login/registration, the guest cart merges with any existing server-side cart — if the same item exists in both, the higher quantity wins.

### Administrator
- **Who**: Internal staff managing the store's catalog, orders, and users.
- **Goals**: Monitor store performance, manage products/categories/orders/users.
- **Access**: All customer-facing pages plus the admin dashboard at `/admin`.
- **Initial admin**: Created via a database seed script with configurable credentials.

### Roles Summary

| Role    | Storefront | Account Area | Admin Dashboard |
|---------|------------|--------------|-----------------|
| Guest   | Yes        | No           | No              |
| Customer| Yes        | Yes          | No              |
| Admin   | Yes        | Yes          | Yes             |

---

## 2. User Stories & Acceptance Criteria

### 2.1 Product Discovery

**US-1: Browse products by category**
- As a customer, I want to browse products organized into categories so I can find what I'm looking for.
- **AC1**: Categories are displayed in a sidebar or top navigation with product counts.
- **AC2**: Categories support up to two nesting levels (e.g., "Electronics > Headphones").
- **AC3**: Clicking a category shows all products in that category.

**US-2: Search for products**
- As a customer, I want to search products by name and description so I can quickly find specific items.
- **AC1**: A search bar is available on every page.
- **AC2**: Results are ranked by relevance.
- **AC3**: If no results match, a friendly "no results" message with suggestions is displayed.

**US-3: Filter and sort product listings**
- As a customer, I want to filter and sort product listings so I can narrow down my choices.
- **AC1**: Filters available: price range, minimum star rating, in-stock only.
- **AC2**: Sort options: price low-to-high, price high-to-low, newest arrivals, most popular (by total units sold).
- **AC3**: Active filters display as removable chips with a "Clear all" action.
- **AC4**: Filter/sort changes update the product list without a full page reload.

### 2.2 Product Details

**US-4: View product detail page**
- As a customer, I want to see full product information so I can make a purchase decision.
- **AC1**: Page shows image gallery (with thumbnail navigation), full description, pricing, category breadcrumb, average rating, and review count.
- **AC2**: If the product has variants, selecting a variant updates the price and stock status.
- **AC3**: "Add to Cart" button is displayed; disabled when out of stock.

**US-5: View and submit product reviews**
- As an authenticated customer who purchased a product, I want to leave a review so I can share my experience.
- **AC1**: Reviews show reviewer name, star rating (1-5), review text, and date.
- **AC2**: A rating distribution summary (1-5 stars) is displayed at the top.
- **AC3**: Reviews are paginated (offset pagination, default page size).
- **AC4**: Only authenticated users who have purchased the product can submit a review.
- **AC5**: Reviews are published immediately (no moderation queue).
- **AC6**: Customers can edit or delete their own reviews. Edited reviews show an "edited" label with timestamp.
- **AC7**: Admins can delete any review from the admin panel.

### 2.3 User Accounts

**US-6: Register an account**
- As a visitor, I want to register so I can place orders and access account features.
- **AC1**: Registration requires email, password, first name, and last name.
- **AC2**: Password must be at least 8 characters with a mix of letters and numbers.
- **AC3**: A password strength indicator provides real-time feedback.
- **AC4**: After registration, the customer is logged in automatically.

**US-7: Log in and log out**
- As a returning customer, I want to log in so I can access my account.
- **AC1**: Login with email and password.
- **AC2**: After 5 failed attempts within 15 minutes, the account is locked for 30 minutes.
- **AC3**: "Forgot password?" sends a reset email; the link is valid for 1 hour and single-use.

**US-8: Manage account profile**
- As a customer, I want to manage my profile and addresses.
- **AC1**: Profile: view and edit name and phone number. Email is read-only in v1.
- **AC2**: Addresses: save up to 5 shipping addresses with labels (e.g., "Home"), mark one as default, edit or delete any.
- **AC3**: Account dashboard at `/account` shows: latest order with status, saved address count, wishlist item count, profile completeness — each linking to the relevant section.

**US-9: Manage wishlist**
- As a customer, I want to save products for later so I can buy them when ready.
- **AC1**: A heart icon on product cards and detail pages toggles wishlist membership.
- **AC2**: Out-of-stock items remain on the wishlist with a clear label.
- **AC3**: Wishlist is accessible from the account area.

### 2.4 Shopping & Checkout

**US-10: Manage shopping cart**
- As a customer, I want to add products to my cart and adjust quantities.
- **AC1**: Adding a product with variants requires selecting a variant first.
- **AC2**: Adding the same product/variant increments quantity (no duplicates).
- **AC3**: Cart icon in the header shows running item count; toast notification on add.
- **AC4**: Cart page shows: item image, name, variant, unit price, quantity adjuster (capped at stock), line total, remove button.
- **AC5**: Cart summary shows subtotal, estimated tax, and total.
- **AC6**: Empty cart shows "Continue Shopping" message.
- **AC7**: Guest carts are stored in localStorage and merge on login/registration (higher quantity wins).

**US-11: Complete checkout**
- As a customer, I want to place an order through a multi-step checkout.
- **AC1**: Checkout requires authentication (guests redirected to login with return URL).
- **AC2**: Step 1 — Shipping address: pick a saved address or enter a new one (option to save it).
- **AC3**: Step 2 — Shipping method: Standard (5-7 days) or Express (2-3 days) at fixed prices. Cheapest pre-selected.
- **AC4**: Step 3 — Payment: Stripe-powered card form. Card data never touches the server. Clear error on failure with retry option.
- **AC5**: Step 4 — Confirmation: order number, items, shipping address, method, payment breakdown (subtotal, shipping, tax, total), estimated delivery date. Cart is cleared. Order appears in history.
- **AC6**: Stock validated on add-to-cart AND at checkout. Out-of-stock items flagged before proceeding. Stock decremented atomically on successful payment.

**US-12: Tax calculation**
- Tax is calculated as a single flat percentage rate applied to all orders.
- The rate is configurable (e.g., a store setting).
- Market: US only. All prices in USD.

### 2.5 Post-Purchase

**US-13: View order history and details**
- As a customer, I want to see my past and current orders.
- **AC1**: Order list sorted newest-first with: order number, date, item count, total, color-coded status badge.
- **AC2**: Order statuses: pending, paid, processing, shipped, delivered, cancelled, refunded.
- **AC3**: Order detail shows: all line items with image/price, shipping address/method, payment summary, step-by-step status timeline.
- **AC4**: Tracking number displayed for shipped orders.

**US-14: Reorder from past orders**
- As a customer, I want to quickly reorder items from a past order.
- **AC1**: "Reorder" button adds all available items (with exact variant selections) back into the cart.
- **AC2**: If a variant is no longer available, that item is skipped with a notification to the customer.

**US-15: Cancel an order**
- As a customer, I want to cancel an order that hasn't shipped yet.
- **AC1**: Cancellation is available when order status is "paid" or "processing".
- **AC2**: Cancellation triggers an automatic Stripe refund.
- **AC3**: Stock for cancelled items is restored.

### 2.6 Admin — Dashboard

**US-16: View store performance**
- As an admin, I want to see key metrics to understand store performance.
- **AC1**: KPIs for last 30 days: total revenue, total orders, average order value, registered customer count.
- **AC2**: Daily revenue chart for the 30-day period.
- **AC3**: Top 5 best-selling products and 5 most recent orders displayed.
- **AC4**: Data is fetched on page load (no real-time updates).

### 2.7 Admin — Product Management

**US-17: Manage products**
- As an admin, I want to create, edit, and deactivate products.
- **AC1**: Product table with thumbnail, name, category, base price, total stock, active/inactive status.
- **AC2**: Table supports search by name, filter by category or status, sort by name/price/creation date.
- **AC3**: Create/edit: name, auto-generated slug (editable), rich-text description, category, base price, active/inactive toggle.
- **AC4**: Images: up to 10 per product (5 MB each), drag-and-drop reorder, alt text. Stored in cloud storage (e.g., AWS S3 or Cloudinary).
- **AC5**: Flat variants: each variant has a name (e.g., "Large / Red"), SKU, optional price override, and stock quantity. No nested attribute system.
- **AC6**: Products are never permanently deleted — only deactivated (hidden from storefront, preserved in database and historical orders).

### 2.8 Admin — Category Management

**US-18: Manage categories**
- As an admin, I want to organize the product catalog into categories.
- **AC1**: Categories displayed as an editable tree (max 2 levels).
- **AC2**: Create root categories or subcategories; edit name, slug, parent; drag-and-drop reorder.
- **AC3**: Cannot delete a category with assigned products — admin must reassign first.
- **AC4**: Moving a product to a different category preserves all its reviews, ratings, and order history.

### 2.9 Admin — Order Management

**US-19: Manage orders**
- As an admin, I want to process and track all customer orders.
- **AC1**: Order table with filter by status (multi-select) and date range.
- **AC2**: Order detail shows same info as customer view, plus customer email and an admin-only notes field.
- **AC3**: Status transitions: paid → processing → shipped (requires tracking number) → delivered.
- **AC4**: Admins can issue refunds on any paid or completed order.
- **AC5**: Every status change is logged with admin identity and timestamp.

### 2.10 Admin — User Management

**US-20: Manage user accounts**
- As an admin, I want to manage customer and admin accounts.
- **AC1**: User table with email, name, role, registration date, order count, active status.
- **AC2**: Promote customer to admin or demote admin to customer (at least one admin must always exist).
- **AC3**: Deactivate or reactivate accounts. Deactivated users are forced to log out on their next request; their data is preserved but inaccessible until reactivation.
- **AC4**: Admins cannot edit another user's profile details — only role and active status.

---

## 3. Data Model Overview

### Key Entities and Relationships

```
User
├── id (PK)
├── email (unique)
├── password_hash
├── first_name
├── last_name
├── phone
├── role (customer | admin)
├── is_active (boolean)
├── created_at
└── updated_at

Address
├── id (PK)
├── user_id (FK → User)
├── label (e.g., "Home", "Office")
├── street, city, state, zip_code, country
├── is_default (boolean)
└── timestamps

Category
├── id (PK)
├── parent_id (FK → Category, nullable, max 2 levels)
├── name
├── slug (unique)
├── sort_order
└── timestamps

Product
├── id (PK)
├── category_id (FK → Category)
├── name
├── slug (unique)
├── description (rich text)
├── base_price (decimal)
├── is_active (boolean)
├── total_units_sold (for popularity sort)
└── timestamps

ProductImage
├── id (PK)
├── product_id (FK → Product)
├── url (cloud storage URL)
├── alt_text
├── sort_order
└── timestamps

ProductVariant
├── id (PK)
├── product_id (FK → Product)
├── name (e.g., "Large / Red")
├── sku (unique)
├── price_override (decimal, nullable — falls back to product base_price)
├── stock_quantity (integer)
└── timestamps

Review
├── id (PK)
├── product_id (FK → Product)
├── user_id (FK → User)
├── rating (1-5)
├── text
├── is_edited (boolean)
├── created_at
└── updated_at

Wishlist (join table)
├── user_id (FK → User)
├── product_id (FK → Product)
└── created_at

Order
├── id (PK)
├── user_id (FK → User)
├── order_number (unique, human-readable)
├── status (pending | paid | processing | shipped | delivered | cancelled | refunded)
├── shipping_address (snapshot — not FK)
├── shipping_method (standard | express)
├── shipping_cost (decimal)
├── subtotal (decimal)
├── tax_amount (decimal)
├── total (decimal)
├── tracking_number (nullable)
├── estimated_delivery_date
├── stripe_payment_intent_id
├── admin_notes (text, nullable)
└── timestamps

OrderItem
├── id (PK)
├── order_id (FK → Order)
├── product_id (FK → Product)
├── variant_id (FK → ProductVariant, nullable)
├── product_name (snapshot)
├── variant_name (snapshot)
├── unit_price (snapshot)
├── quantity
└── line_total

OrderStatusLog
├── id (PK)
├── order_id (FK → Order)
├── old_status
├── new_status
├── changed_by (FK → User, admin)
├── timestamp

Cart (server-side, for authenticated users)
├── id (PK)
├── user_id (FK → User)
└── timestamps

CartItem
├── id (PK)
├── cart_id (FK → Cart)
├── product_id (FK → Product)
├── variant_id (FK → ProductVariant, nullable)
├── quantity
└── timestamps

StoreSetting (key-value for configurable values)
├── key (e.g., "tax_rate", "standard_shipping_price", "express_shipping_price")
├── value
└── updated_at
```

### Key Relationships
- **User** has many **Addresses** (max 5), **Orders**, **Reviews**, and **Wishlist** entries.
- **Category** self-references for nesting (max 2 levels). Has many **Products**.
- **Product** has many **ProductImages**, **ProductVariants**, and **Reviews**.
- **Order** has many **OrderItems** and **OrderStatusLogs**. Contains a snapshot of the shipping address (not a live reference).
- **OrderItem** stores snapshots of product/variant names and prices at time of purchase.
- **Cart** has many **CartItems**. Guest carts live in browser localStorage.

---

## 4. Feature List with Priorities

### MVP (v1) — Must Have

| #  | Feature                        | Description                                                                 |
|----|--------------------------------|-----------------------------------------------------------------------------|
| 1  | Product catalog browsing       | Categories (2-level), product listings with images and pricing              |
| 2  | Product search                 | Full-text search on name and description, ranked by relevance               |
| 3  | Filtering & sorting            | Price range, rating, stock filters; price/newest/popularity sort            |
| 4  | Product detail pages           | Gallery, description, pricing, variants, stock status, breadcrumbs          |
| 5  | Product variants               | Flat variant model: name, SKU, optional price override, stock quantity      |
| 6  | User registration & login      | Email/password auth, password strength indicator, account lockout, password reset |
| 7  | User profile & addresses       | Edit name/phone, manage up to 5 shipping addresses                         |
| 8  | Shopping cart                   | Add/remove/adjust items, guest cart with merge on login                     |
| 9  | Multi-step checkout            | Shipping address → shipping method → Stripe payment → confirmation         |
| 10 | Flat tax calculation           | Single configurable tax rate applied to all orders                          |
| 11 | Order management (customer)    | Order history, detail view, status timeline, tracking number               |
| 12 | Order cancellation             | Customer-initiated cancel (before shipping) with auto-refund               |
| 13 | Reorder                        | Re-add items from past order with exact variants; skip unavailable items    |
| 14 | Product reviews                | Submit/edit/delete reviews (verified purchasers), rating summary, pagination|
| 15 | Wishlist                       | Add/remove products, persist out-of-stock items with label                 |
| 16 | Admin dashboard                | Revenue, orders, AOV, customer KPIs; daily revenue chart; top products     |
| 17 | Admin product management       | CRUD (soft-delete), images (cloud storage), variants, rich-text description|
| 18 | Admin category management      | Tree editor, 2-level nesting, drag-and-drop reorder, reassign guard        |
| 19 | Admin order management         | Status transitions, tracking numbers, refunds, admin notes, audit log      |
| 20 | Admin user management          | Role promotion/demotion, account deactivation/reactivation                 |
| 21 | Stock management               | Atomic stock decrement on payment, validation at add-to-cart and checkout  |

### Out of Scope for v1 (Explicitly Deferred)

- Social or OAuth login (Google, GitHub, etc.)
- Two-factor authentication
- Email verification on registration
- Account deletion or GDPR data export
- Product recommendations ("Customers also bought")
- Product comparison
- Multi-language product descriptions
- Multi-currency support
- Promo codes, coupons, and discounts
- Saved payment methods or digital wallets (Apple Pay, PayPal)
- Subscription or recurring orders
- Order editing after placement
- Real-time tax calculation via third-party service
- Email notifications for order status changes
- Returns and exchanges
- Invoice or receipt PDF generation
- Customer-admin messaging on orders
- Gift cards and store credit
- Bulk product import/export
- In-browser image cropping or resizing
- Low-stock alerts
- CMS or page content management
- Multi-level admin permissions (all admins have equal access)

---

## 5. Scope Boundaries

### In Scope
- Single-region (US) ecommerce store with USD pricing
- Two user roles: Customer and Admin (equal admin permissions)
- Stripe as the sole payment processor
- Cloud storage (e.g., S3/Cloudinary) for product images
- Flat tax rate (configurable store setting)
- Fixed shipping rates: Standard (5-7 days) and Express (2-3 days)
- Guest browsing and cart with merge-on-login
- Soft-delete pattern for products and user accounts
- Database seed script for initial admin creation
- Offset-based pagination throughout (20 items for product listings, 25 rows for admin tables)
- Server-side cart for authenticated users, localStorage cart for guests

### Out of Scope
- Everything listed in "Out of Scope for v1" above
- Mobile native apps (web application only)
- Real-time features (WebSockets, live dashboards)
- Third-party integrations beyond Stripe
- Multi-tenant or marketplace functionality
- Inventory management beyond simple stock counts
- Analytics beyond the admin dashboard KPIs

---

## 6. Clarification Decisions Log

| Question | Decision |
|----------|----------|
| Tax calculation approach | Single flat configurable tax rate |
| Geographic market | US only, USD currency |
| First admin creation | Database seed script with configurable credentials |
| Product image storage | Cloud storage (S3/Cloudinary) |
| Review moderation | Immediate publish; admins can delete |
| Account deactivation behavior | Force logout on next request; data preserved |
| Guest reviews | Not allowed; only authenticated purchasers |
| "Most popular" sort metric | Total units sold |
| Review editing | Customers can edit and delete own reviews; "edited" label shown |
| Variant structure | Flat (name + SKU + optional price override + stock) |
| Category reassignment impact | Preserves all reviews, ratings, and order history |
| Dashboard data freshness | Fetched on page load (no real-time) |
| Pagination style | Offset pagination (page numbers) |
| Default page sizes | 20 items for product listings, 25 rows for admin tables |
| Reorder behavior | Exact variant selections; unavailable items skipped with notification |

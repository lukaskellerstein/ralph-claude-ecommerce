# Feature Specification: Admin Dashboard

| Field          | Value                          |
|----------------|--------------------------------|
| Feature Branch | 005-admin-dashboard            |
| Created        | 2026-04-14                     |
| Status         | Draft                          |

## 1. Overview

The admin dashboard provides store operators with tools to manage the product catalog, process orders, and view business analytics. It is a protected section of the application accessible only to users with the `admin` role. The admin interface lives under the `/admin` route and shares the same backend API with additional admin-only endpoints.

## 2. User Stories

### US-001: Admin Login and Access Control

**As an** admin,
**I want to** access the admin dashboard using my admin account,
**So that** I can manage the store.

**Acceptance Criteria:**

- Admin dashboard is accessible at `/admin`.
- Only users with `role = admin` can access `/admin` routes. Non-admin users see a 403 page.
- Admin uses the same login flow as customers (spec 002) — no separate login page.
- After login, admins see an "Admin" link in the header navigation.
- Admin API endpoints return 403 for non-admin JWT tokens.

**Independent Test:** Can be fully tested by logging in as admin and verifying dashboard access, then logging in as a regular user and verifying the 403 response on admin routes.

### US-002: Manage Products (CRUD)

**As an** admin,
**I want to** create, edit, and deactivate products,
**So that** I can maintain the store's catalog.

**Acceptance Criteria:**

- Product list page shows all products in a data table with columns: image thumbnail, name, category, base price, stock (total across variants), status (active/inactive), and actions.
- Data table supports search (by product name), filtering (by category, status), and sorting (by name, price, date created).
- "Create Product" button opens a form with: name, slug (auto-generated from name, editable), description (rich text editor), category selector, base price, and status toggle.
- Edit product form is pre-filled with existing data.
- Product images: admin can upload multiple images, reorder them via drag-and-drop, and set alt text. [NEEDS CLARIFICATION: Image storage — local filesystem or cloud storage (S3/R2) in v1?]
- Product variants: admin can add/edit/remove variants with fields: variant name (e.g., "Large / Red"), SKU, price override (optional, defaults to base price), stock quantity.
- "Deactivate" sets the product to inactive — it no longer appears in the storefront but is preserved in the database and in past orders.
- There is no hard delete for products.
- Admin product endpoints: `GET/POST /api/v1/admin/products`, `PATCH /api/v1/admin/products/:id`, image upload via `POST /api/v1/admin/products/:id/images`.

**Independent Test:** Can be fully tested by creating a new product with images and variants, editing its name and price, deactivating it, and verifying it no longer appears on the storefront.

### US-003: Manage Categories

**As an** admin,
**I want to** create, edit, and delete categories,
**So that** products are organized logically for customers.

**Acceptance Criteria:**

- Category management page shows a tree view of categories (parent → children).
- Admin can create a new root category or a subcategory under an existing one.
- Category form fields: name, slug, description (optional), parent category (optional, dropdown).
- Admin can edit category name, slug, and parent.
- Deleting a category is only allowed if it has no products assigned. Otherwise, a warning prompts reassignment.
- Reordering categories (display order) is supported via drag-and-drop or position number.
- Admin category endpoints: `GET/POST /api/v1/admin/categories`, `PATCH/DELETE /api/v1/admin/categories/:id`.

**Independent Test:** Can be fully tested by creating a parent category, adding a child, assigning a product to the child, attempting to delete the child (expecting a warning), reassigning the product, then deleting successfully.

### US-004: Manage Orders

**As an** admin,
**I want to** view all orders and update their status,
**So that** I can process and fulfill customer orders.

**Acceptance Criteria:**

- Order management page shows all orders (across all users) in a data table with columns: order number, customer name, date placed, total, status, and actions.
- Data table supports filtering by status (multi-select) and date range.
- Clicking an order opens the order detail view with all information from spec 004, plus: customer email, admin-only notes field.
- Admin can update order status via a dropdown with valid transitions: `paid → processing`, `processing → shipped` (with tracking number input), `shipped → delivered`.
- Admin can add a tracking number when changing status to `shipped`.
- Admin can initiate a refund for any paid/completed order. The refund creates a Stripe refund and sets the order status to `refunded`.
- Status changes are logged in an order status history with the admin user and timestamp.
- Admin order endpoints: `GET /api/v1/admin/orders`, `GET /api/v1/admin/orders/:id`, `PATCH /api/v1/admin/orders/:id/status`, `POST /api/v1/admin/orders/:id/refund`.

**Independent Test:** Can be fully tested by viewing all orders, filtering by `paid` status, advancing an order to `shipped` with a tracking number, then initiating a refund on another order and verifying the Stripe refund.

### US-005: View Analytics Dashboard

**As an** admin,
**I want to** see key business metrics at a glance,
**So that** I can understand store performance and make decisions.

**Acceptance Criteria:**

- Dashboard home (`/admin`) shows summary KPI cards: total revenue (last 30 days), total orders (last 30 days), average order value, total registered customers.
- A revenue chart shows daily revenue for the last 30 days (line or bar chart).
- A "Top Products" section lists the 5 best-selling products by order count in the last 30 days.
- A "Recent Orders" section shows the 5 most recent orders with status.
- All metrics are computed from the database — no third-party analytics service required in v1.
- Dashboard data endpoint: `GET /api/v1/admin/dashboard/stats`.

[NEEDS CLARIFICATION: Should the time range for KPIs be configurable (e.g., 7/30/90 days), or fixed to 30 days for v1?]

**Independent Test:** Can be fully tested by seeding orders across different dates and verifying the KPI values and chart data match expected calculations.

### US-006: Manage Users

**As an** admin,
**I want to** view registered users and manage their roles,
**So that** I can grant admin access or deactivate problematic accounts.

**Acceptance Criteria:**

- User management page shows all users in a data table with columns: email, name, role, registration date, order count, active status.
- Admin can change a user's role between `customer` and `admin`.
- Admin can deactivate a user account (soft disable — user cannot log in but data is preserved).
- Admin can reactivate a deactivated account.
- Admin CANNOT delete user accounts (data preservation).
- Admin CANNOT edit other user's profile details (name, email) — only role and active status.
- Admin user endpoints: `GET /api/v1/admin/users`, `PATCH /api/v1/admin/users/:id` (role, active).

**Independent Test:** Can be fully tested by viewing users, promoting a user to admin, verifying they can access the admin dashboard, then deactivating a user and verifying they cannot log in.

## 3. Functional Requirements

- **FR-001:** System MUST restrict all `/api/v1/admin/*` endpoints to users with `role = admin`.
- **FR-002:** System MUST support full CRUD for products with soft-delete (deactivation, not deletion).
- **FR-003:** System MUST support image upload for products with a maximum of 10 images per product and 5MB per image.
- **FR-004:** System MUST enforce valid order status transitions and reject invalid ones with a 422 response.
- **FR-005:** System MUST log all order status changes in an audit history with actor and timestamp.
- **FR-006:** System MUST compute dashboard analytics from order and user data with results cached for 5 minutes.
- **FR-007:** System MUST support Stripe refund initiation from the admin panel.
- **FR-008:** System MUST prevent the last admin user from being demoted or deactivated (at least one admin must always exist).
- **FR-009:** System MUST auto-generate product slugs from the product name, with conflict resolution (append numeric suffix).
- **FR-010:** System MUST validate that category hierarchies do not exceed 2 levels of nesting.

## 4. Core Entities (What, Not How)

- **Product:** (Extended) Admin manages all fields including status and images.
- **Category:** (Extended) Admin manages hierarchy and ordering.
- **Order:** (Extended) Admin can update status and add tracking numbers.
- **OrderStatusHistory:** Audit log for status transitions — actor (admin user ID or "system"), previous status, new status, timestamp, optional note.
- **DashboardStats:** Computed/cached aggregate: revenue, order counts, top products, customer count.

## 5. Success Criteria

- **SC-001:** Admin can create a complete product (with images, variants) in under 5 minutes.
- **SC-002:** Order status updates reflect on the customer's order page within 30 seconds.
- **SC-003:** Dashboard analytics load in under 3 seconds.
- **SC-004:** Admin product data table handles 1000+ products without UI lag (virtual scrolling or server-side pagination).

## 6. Assumptions and Dependencies

- **Depends on:** Spec 001 (product/category data model), Spec 002 (user roles), Spec 003 (order data model), Spec 004 (order status tracking).
- The first admin user is created via a database seed script or CLI command — not through the registration flow.
- Image processing (resize, thumbnail generation) is out of scope for v1 — images are stored and served as-is.
- Export to CSV/Excel is out of scope for v1.

## 7. Out of Scope

- Bulk product import/export (CSV/Excel).
- Product image cropping/resizing in the browser.
- Admin audit log beyond order status changes.
- Multi-admin permissions (all admins have the same access level).
- Inventory alerts / low-stock notifications.
- CMS / page content management.
- Discount / coupon management (deferred).

## 8. Review & Acceptance Checklist

- [ ] All user stories have clear acceptance criteria
- [ ] Functional requirements are testable and unambiguous
- [ ] No implementation details leaked into the spec (tech-agnostic "what")
- [ ] All ambiguities marked with [NEEDS CLARIFICATION]
- [ ] Success criteria are measurable
- [ ] Out of scope items are explicitly listed
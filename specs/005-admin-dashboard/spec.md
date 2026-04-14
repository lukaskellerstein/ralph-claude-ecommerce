# Feature Specification: Admin Dashboard

**Feature Branch**: `005-admin-dashboard`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: User description: "Admin dashboard — product CRUD, category management, order processing, business analytics, user management for store operators"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Login and Access Control (Priority: P1)

As a store operator with an admin account, I want to access the admin dashboard using my existing credentials so that I can manage the store without a separate login system.

**Why this priority**: Access control is the foundation — no admin feature works without verifying the user has admin privileges. This gates all other admin functionality.

**Independent Test**: Can be fully tested by logging in as an admin and verifying dashboard access, then logging in as a regular customer and verifying a "forbidden" page is shown when attempting to access admin routes.

**Acceptance Scenarios**:

1. **Given** a user with the admin role, **When** they log in, **Then** an "Admin" link appears in the header navigation.
2. **Given** an admin user, **When** they navigate to the admin area, **Then** the admin dashboard loads successfully.
3. **Given** a user with the customer role, **When** they attempt to navigate to any admin route, **Then** they see a "forbidden" page and cannot access admin content.
4. **Given** an unauthenticated visitor, **When** they attempt to access an admin route, **Then** they are redirected to the login page.
5. **Given** any admin-only backend endpoint, **When** a request arrives with a non-admin session, **Then** the system returns a 403 Forbidden response.

---

### User Story 2 - Manage Products (CRUD) (Priority: P1)

As an admin, I want to create, edit, and deactivate products so that I can maintain the store's catalog with accurate information, images, and variants.

**Why this priority**: Product management is the core admin function — the store cannot operate without the ability to add and maintain products.

**Independent Test**: Can be fully tested by creating a new product with images and variants, editing its name and price, deactivating it, and verifying it no longer appears on the customer-facing storefront.

**Acceptance Scenarios**:

1. **Given** the product list page, **When** the admin views it, **Then** all products are shown in a data table with image thumbnail, name, category, base price, total stock, status, and action buttons.
2. **Given** the product data table, **When** the admin searches by name, filters by category or status, or sorts by column, **Then** the table updates to show matching results.
3. **Given** the "Create Product" button, **When** the admin clicks it, **Then** a form appears with fields for name, slug (auto-generated, editable), description (rich text), category, base price, and status toggle.
4. **Given** the product creation form, **When** the admin submits valid data, **Then** the product is created and appears in the product list.
5. **Given** the product slug field, **When** a slug conflict exists, **Then** the system auto-appends a numeric suffix to make it unique.
6. **Given** the image upload section, **When** the admin uploads images, **Then** the images appear in a reorderable list with drag-and-drop, and alt text can be set for each image.
7. **Given** the variants section, **When** the admin adds a variant, **Then** fields for variant name, SKU, optional price override, and stock quantity are provided.
8. **Given** a product, **When** the admin clicks "Deactivate", **Then** the product is marked inactive — it no longer appears on the storefront but is preserved in the database and past orders.
9. **Given** there is a maximum of 10 images per product, **When** the admin tries to upload an 11th, **Then** the upload is rejected with a clear message.
10. **Given** a maximum file size of 5MB per image, **When** the admin uploads a larger file, **Then** the upload is rejected with a size limit message.

---

### User Story 3 - Manage Categories (Priority: P2)

As an admin, I want to create, edit, reorder, and delete categories so that products are organized logically for customers browsing the store.

**Why this priority**: Category management supports product organization but is less frequently used than day-to-day product and order management.

**Independent Test**: Can be fully tested by creating a parent category, adding a child category, assigning a product, attempting to delete the child (expecting a warning), reassigning the product, then deleting successfully.

**Acceptance Scenarios**:

1. **Given** the category management page, **When** the admin views it, **Then** categories are displayed as a tree (parent → children).
2. **Given** a "Create Category" action, **When** the admin fills in name, slug, and optionally selects a parent, **Then** the category is created in the correct position in the tree.
3. **Given** a category with products assigned, **When** the admin attempts to delete it, **Then** a warning prompts the admin to reassign the products first.
4. **Given** a category with no products, **When** the admin deletes it, **Then** the category is removed from the tree.
5. **Given** the category tree, **When** the admin drags a category to a new position, **Then** the display order is updated.
6. **Given** a three-level nesting attempt (grandchild under a child), **When** the admin tries to create it, **Then** the system rejects it — maximum 2 levels of nesting.

---

### User Story 4 - Manage Orders (Priority: P1)

As an admin, I want to view all orders across all customers and update their status so that I can process and fulfill customer orders efficiently.

**Why this priority**: Order processing is a daily operational task — orders must be fulfilled to keep the business running.

**Independent Test**: Can be fully tested by viewing all orders, filtering by "paid" status, advancing an order to "shipped" with a tracking number, then initiating a refund on another order and verifying the refund.

**Acceptance Scenarios**:

1. **Given** the order management page, **When** the admin views it, **Then** all orders across all customers are shown with order number, customer name, date, total, status, and actions.
2. **Given** the order data table, **When** the admin filters by status or date range, **Then** the table shows only matching orders.
3. **Given** an order detail view, **When** the admin opens it, **Then** all order information is displayed plus customer email and an admin-only notes field.
4. **Given** an order with status "paid", **When** the admin selects "Processing" from the status dropdown, **Then** the status is updated and logged in the status history.
5. **Given** an order transitioning to "shipped", **When** the admin updates the status, **Then** a tracking number input is required before the transition can be saved.
6. **Given** any status change, **When** it completes, **Then** the change is logged in the order status history with the admin's identity and timestamp.
7. **Given** an order with status "paid" or later, **When** the admin initiates a refund, **Then** a full refund is processed through the payment provider and the order status is updated to "refunded".
8. **Given** an invalid status transition (e.g., "delivered" → "paid"), **When** the admin attempts it, **Then** the system rejects it with an error message.

---

### User Story 5 - View Analytics Dashboard (Priority: P2)

As an admin, I want to see key business metrics at a glance so that I can understand store performance and make informed decisions.

**Why this priority**: Analytics provide business insight but are not required for day-to-day store operations. The store can function without them.

**Independent Test**: Can be fully tested by seeding orders across different dates, navigating to the dashboard, and verifying KPI values and chart data match expected calculations.

**Acceptance Scenarios**:

1. **Given** the admin dashboard home, **When** the admin views it, **Then** KPI cards display: total revenue (last 30 days), total orders (last 30 days), average order value, and total registered customers.
2. **Given** the dashboard, **When** the admin views the revenue chart, **Then** a daily revenue chart for the last 30 days is displayed.
3. **Given** the dashboard, **When** the admin views "Top Products", **Then** the 5 best-selling products by order count in the last 30 days are listed.
4. **Given** the dashboard, **When** the admin views "Recent Orders", **Then** the 5 most recent orders with status are shown.
5. **Given** a time range selector, **When** the admin selects 7 days, 30 days, or 90 days, **Then** all KPIs and charts update to reflect the selected period.
6. **Given** dashboard data, **When** it was computed more than 5 minutes ago, **Then** the system recomputes and serves fresh data.

---

### User Story 6 - Manage Users (Priority: P3)

As an admin, I want to view registered users and manage their roles and account status so that I can grant admin access or handle problematic accounts.

**Why this priority**: User management is an infrequent administrative task. Most stores rarely need to change user roles or deactivate accounts.

**Independent Test**: Can be fully tested by viewing users, promoting a customer to admin (verifying they gain admin access), deactivating a user (verifying they cannot log in), then reactivating them.

**Acceptance Scenarios**:

1. **Given** the user management page, **When** the admin views it, **Then** all users are listed with email, name, role, registration date, order count, and active status.
2. **Given** a customer user, **When** the admin changes their role to admin, **Then** the user can access the admin dashboard on their next login.
3. **Given** an active user, **When** the admin deactivates their account, **Then** the user cannot log in but their data (orders, reviews) is preserved.
4. **Given** a deactivated user, **When** the admin reactivates their account, **Then** the user can log in again.
5. **Given** the last remaining admin user, **When** the admin attempts to demote or deactivate them, **Then** the system blocks the action with a clear error message.
6. **Given** any user, **When** the admin views their row, **Then** the admin cannot edit the user's name, email, or password — only role and active status.

---

### Edge Cases

- What happens when the admin deactivates a product that is in someone's cart? The product remains in the cart but is flagged as unavailable at checkout (handled by Spec 003 stock validation).
- What happens when the admin deletes a category that has subcategories? The subcategories are orphaned and promoted to root level, or the deletion is blocked. Assumption: deletion is blocked if the category has subcategories.
- What happens when the admin tries to refund an already-refunded order? The system shows the order is already refunded and disables the refund action.
- What happens if two admins update the same order status simultaneously? The status state machine prevents invalid transitions — the second update will fail if the status has already changed.
- What happens when the admin uploads an image in an unsupported format? The system rejects it with a message listing accepted formats (JPEG, PNG, WebP).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST restrict all admin-area endpoints to users with the admin role, returning 403 Forbidden for non-admin users.
- **FR-002**: System MUST support product creation with name, slug, description, category, base price, status, images, and variants.
- **FR-003**: System MUST auto-generate product slugs from the product name with conflict resolution (append numeric suffix if duplicate exists).
- **FR-004**: System MUST support product image upload with a maximum of 10 images per product, 5MB maximum per image, and accepted formats (JPEG, PNG, WebP).
- **FR-005**: System MUST support image reordering (position) and alt text editing.
- **FR-006**: System MUST support product variant management: add, edit, remove variants with variant name, SKU, optional price override, and stock quantity.
- **FR-007**: System MUST support product deactivation (soft disable) — deactivated products are hidden from the storefront but preserved in the database.
- **FR-008**: System MUST support category CRUD with tree hierarchy (maximum 2 levels), display ordering, and deletion protection when products are assigned.
- **FR-009**: System MUST block category deletion when subcategories exist.
- **FR-010**: System MUST display all orders across all customers with filtering by status and date range.
- **FR-011**: System MUST enforce valid order status transitions via the same state machine as Spec 004 and reject invalid transitions.
- **FR-012**: System MUST require a tracking number when transitioning an order to "shipped" status.
- **FR-013**: System MUST support admin-initiated refunds through the payment provider for paid or completed orders.
- **FR-014**: System MUST log all order status changes with the admin's identity and timestamp.
- **FR-015**: System MUST compute and display dashboard analytics: total revenue, order count, average order value, customer count, daily revenue chart, top products — with configurable time range (7, 30, 90 days).
- **FR-016**: System MUST cache dashboard analytics for 5 minutes to avoid repeated expensive queries.
- **FR-017**: System MUST support user role changes (customer ↔ admin) and account activation/deactivation.
- **FR-018**: System MUST prevent the last admin user from being demoted or deactivated.

### Key Entities

- **Product** (extended from Spec 001): Admin manages all fields including status, images, and variants. No new entity — uses existing Product, ProductImage, ProductVariant models.
- **Category** (extended from Spec 001): Admin manages hierarchy and display ordering. No new entity.
- **Order** (extended from Specs 003/004): Admin can update status, add tracking number, initiate refund. No new entity.
- **OrderStatusHistory** (from Spec 004): Logs admin-triggered status changes with actor_type='admin'.
- **DashboardStats**: A computed, cached aggregate — not a persistent entity. Contains: total revenue, order count, average order value, customer count, daily revenue breakdown, top products list.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An admin can create a complete product (with images and variants) in under 5 minutes.
- **SC-002**: Order status updates made by an admin are reflected on the customer's order page within 30 seconds.
- **SC-003**: Dashboard analytics page loads and displays all metrics within 3 seconds.
- **SC-004**: The product data table remains responsive (scrolling, filtering, sorting) with 1,000+ products.
- **SC-005**: 95% of admin users can locate and update a specific order's status within 60 seconds.
- **SC-006**: Admin-initiated refunds are processed and confirmed within 10 seconds.

## Assumptions

- The admin role already exists on the User entity (from Spec 002 with role field: 'customer' or 'admin').
- The first admin user is created via a database seed script or CLI command — not through the customer registration flow.
- Product, Category, and Order data models exist from Specs 001, 003, and 004. This spec extends them with admin management capabilities.
- Image storage uses the local filesystem in v1. Images are stored as-is without server-side processing (no resize, thumbnail generation, or format conversion).
- Accepted image formats: JPEG, PNG, WebP.
- The admin dashboard is part of the same frontend application, served under the `/admin` route — not a separate application.
- All admins have the same access level. Multi-tier admin permissions (e.g., "editor" vs "super admin") are out of scope.
- Dashboard analytics time range is configurable: 7, 30, or 90 days, defaulting to 30 days.
- Dashboard analytics are cached server-side for 5 minutes to avoid repeated expensive queries.
- Rich text editing for product descriptions uses a standard editor component (e.g., markdown or WYSIWYG).
- Product slug auto-generation: lowercase, hyphens replace spaces, special characters stripped. On conflict, append `-2`, `-3`, etc.
- Category deletion is blocked if the category has either products or subcategories assigned.

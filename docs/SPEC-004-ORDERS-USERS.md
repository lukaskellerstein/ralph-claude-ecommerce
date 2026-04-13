# Feature Specification: Order Management & User Account

| Field          | Value                          |
|----------------|--------------------------------|
| Feature Branch | 004-order-management           |
| Created        | 2026-04-14                     |
| Status         | Draft                          |

## 1. Overview

Order management provides customers with visibility into their past and current orders, including status tracking from payment through delivery. This spec also covers the user account hub that ties together profile, addresses, orders, and wishlist into a unified account experience.

## 2. User Stories

### US-001: View Order History

**As a** logged-in customer,
**I want to** see a list of all my past and current orders,
**So that** I can track purchases and find order details.

**Acceptance Criteria:**

- Order history page is accessible from the user account menu at `/account/orders`.
- Orders are listed in reverse chronological order (newest first).
- Each order row shows: order number, date placed, number of items, total amount, and current status.
- Status is displayed with a color-coded badge: `pending` (yellow), `paid` (blue), `processing` (blue), `shipped` (purple), `delivered` (green), `cancelled` (red), `refunded` (gray).
- List is paginated with cursor-based pagination (10 orders per page).
- Orders endpoint: `GET /api/v1/orders`.

**Independent Test:** Can be fully tested by placing 2+ orders, navigating to order history, and verifying all orders appear in correct chronological order with accurate details.

### US-002: View Order Detail

**As a** customer,
**I want to** view the full details of a specific order,
**So that** I can see exactly what I purchased, where it's being shipped, and its current status.

**Acceptance Criteria:**

- Order detail page is accessible at `/account/orders/:order_number`.
- Page displays: order number, date placed, status with timeline/stepper visualization, list of items (image, name, variant, quantity, unit price, line total), shipping address, shipping method, payment summary (subtotal, shipping, tax, total), and Stripe payment status.
- If the order is shipped, a tracking number is displayed (if available). [NEEDS CLARIFICATION: Will tracking numbers be entered manually by admin, or integrated with a shipping provider API?]
- A "Reorder" button adds all items from this order to the current cart. If any item is unavailable, a warning is shown for those items.
- Order detail endpoint: `GET /api/v1/orders/:order_number`.

**Independent Test:** Can be fully tested by navigating to a known order and verifying all fields match the original purchase, then clicking "Reorder" and verifying items are added to the cart.

### US-003: Cancel a Pending Order

**As a** customer,
**I want to** cancel an order that has not yet been shipped,
**So that** I can change my mind without contacting support.

**Acceptance Criteria:**

- A "Cancel Order" button is visible on the order detail page only when order status is `paid` or `processing`.
- Clicking the button shows a confirmation dialog: "Are you sure you want to cancel this order?"
- On confirmation, the order status changes to `cancelled` and a Stripe refund is initiated.
- The refund is processed via the Stripe Refunds API.
- Stock quantities are restored for cancelled items.
- Cancel endpoint: `POST /api/v1/orders/:order_number/cancel`.

**Independent Test:** Can be fully tested by placing an order, cancelling it before shipment, and verifying the status updates to `cancelled`, the refund appears in Stripe test dashboard, and stock is restored.

### US-004: Manage Wishlist

**As a** logged-in customer,
**I want to** save products to a wishlist,
**So that** I can keep track of items I want to buy later.

**Acceptance Criteria:**

- A heart/bookmark icon on product cards and product detail pages toggles wishlist status.
- Wishlist page is accessible at `/account/wishlist`.
- Wishlist shows product cards with: image, name, price, stock status, and "Add to Cart" and "Remove" actions.
- If a wishlisted product goes out of stock, it remains on the wishlist with a clear "Out of Stock" label.
- Wishlist is unlimited in size for v1.
- Wishlist endpoints: `GET /api/v1/users/me/wishlist`, `POST /api/v1/users/me/wishlist` (add), `DELETE /api/v1/users/me/wishlist/:product_id` (remove).

**Independent Test:** Can be fully tested by adding a product to the wishlist from the product page, verifying it appears on the wishlist page, then removing it and verifying it disappears.

### US-005: Account Dashboard

**As a** logged-in customer,
**I want to** see a dashboard overview when I access my account,
**So that** I can quickly navigate to my orders, addresses, profile, and wishlist.

**Acceptance Criteria:**

- Account dashboard is at `/account`.
- Dashboard shows summary cards for: recent order (last order with status), number of saved addresses, wishlist item count, and profile completeness (name + phone filled in).
- Each card links to the relevant section.
- Navigation sidebar (on desktop) or tab bar (on mobile) provides access to: Orders, Addresses, Wishlist, Profile, and a Log Out action.

**Independent Test:** Can be fully tested by logging in and navigating to `/account`, verifying all summary cards show accurate data and link to the correct pages.

## 3. Functional Requirements

- **FR-001:** System MUST return paginated order history for the authenticated user via `GET /api/v1/orders`.
- **FR-002:** System MUST return full order details including items, address snapshot, and payment info via `GET /api/v1/orders/:order_number`.
- **FR-003:** System MUST restrict order access — users can only view their own orders.
- **FR-004:** System MUST allow order cancellation only when status is `paid` or `processing`.
- **FR-005:** System MUST initiate a Stripe refund on order cancellation and update status to `cancelled`.
- **FR-006:** System MUST restore stock quantities when an order is cancelled.
- **FR-007:** System MUST support a user wishlist with add/remove/list operations.
- **FR-008:** System MUST prevent duplicate wishlist entries (adding an already-wishlisted product is a no-op).
- **FR-009:** Order status transitions MUST follow: `pending → paid → processing → shipped → delivered` or `pending/paid/processing → cancelled`. No other transitions are valid.
- **FR-010:** System MUST support a "reorder" action that adds all available items from a past order to the cart.

## 4. Core Entities (What, Not How)

- **Order:** (Extended from spec 003) Adds status tracking, tracking number, cancellation timestamp.
- **OrderStatusHistory:** A log of all status changes for an order, with timestamp and actor (system or admin).
- **WishlistItem:** Links a user to a product. No variant — wishlist is at the product level.

## 5. Success Criteria

- **SC-001:** Users can find a specific past order within 10 seconds.
- **SC-002:** Order cancellation and refund initiation completes within 5 seconds.
- **SC-003:** Wishlist toggle (add/remove) responds in under 200ms.
- **SC-004:** Order status updates are reflected in the UI within 30 seconds of the backend change.

## 6. Assumptions and Dependencies

- **Depends on:** Spec 002 (user authentication), Spec 003 (orders are created via checkout).
- Order status transitions beyond `paid` are triggered by admin actions (spec 005) or webhook events.
- Email notifications for order status changes are out of scope for v1.
- Tracking number integration with carriers is out of scope — tracking numbers are plain text entered by admin.

## 7. Out of Scope

- Email notifications for order status changes.
- Returns and exchanges workflow.
- Invoice/receipt PDF generation.
- Order notes or communication between customer and admin.
- Gift cards and store credit.

## 8. Review & Acceptance Checklist

- [ ] All user stories have clear acceptance criteria
- [ ] Functional requirements are testable and unambiguous
- [ ] No implementation details leaked into the spec (tech-agnostic "what")
- [ ] All ambiguities marked with [NEEDS CLARIFICATION]
- [ ] Success criteria are measurable
- [ ] Out of scope items are explicitly listed
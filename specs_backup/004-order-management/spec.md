# Feature Specification: Order Management & User Account

**Feature Branch**: `004-order-management`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: User description: "Order management with order history, order detail, order cancellation with refund, wishlist, and account dashboard"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Order History (Priority: P1)

As a logged-in customer, I want to see a list of all my past and current orders so that I can track purchases and find order details quickly.

**Why this priority**: Order history is the foundational feature of the account area. Without it, customers cannot track or reference any previous purchases.

**Independent Test**: Can be fully tested by placing 2+ orders, navigating to the order history page, and verifying all orders appear in reverse chronological order with correct order numbers, dates, item counts, totals, and color-coded status badges.

**Acceptance Scenarios**:

1. **Given** a customer with 3 past orders, **When** they navigate to the order history page, **Then** all 3 orders appear listed newest first, each showing order number, date, item count, total, and status badge.
2. **Given** an order with status "paid", **When** the customer views the order list, **Then** the status is shown as a blue badge with the text "Paid".
3. **Given** more than 10 orders, **When** the customer scrolls to the bottom, **Then** a "Load More" control fetches the next page of orders.
4. **Given** a customer with no orders, **When** they visit the order history page, **Then** a friendly empty state is shown with a "Start Shopping" link.
5. **Given** an unauthenticated visitor, **When** they try to access the order history page, **Then** they are redirected to the login page with a return URL.

---

### User Story 2 - View Order Detail (Priority: P1)

As a customer, I want to view the full details of a specific order so that I can see exactly what I purchased, where it's being shipped, and its current status.

**Why this priority**: Order detail is tightly coupled with order history — customers expect to drill into any order from the list. It also provides the context needed for cancellation and reordering.

**Independent Test**: Can be fully tested by navigating to a known order's detail page and verifying all fields (order number, date, status timeline, items with images and prices, shipping address, shipping method, payment summary) match the original purchase.

**Acceptance Scenarios**:

1. **Given** an order with 2 items, **When** the customer views the order detail, **Then** both items are shown with product image, name, variant, quantity, unit price, and line total.
2. **Given** an order detail page, **When** the customer views the status section, **Then** a timeline/stepper shows the order's progression through statuses with timestamps.
3. **Given** a shipped order with a tracking number, **When** the customer views the order detail, **Then** the tracking number is displayed as plain text.
4. **Given** an order detail page, **When** the customer views the payment summary, **Then** subtotal, shipping cost, tax, and total are displayed correctly.
5. **Given** any order, **When** the customer clicks "Reorder", **Then** all available items from that order are added to the cart, and a warning is shown for any items that are out of stock or no longer available.
6. **Given** an order that belongs to another user, **When** a customer tries to access it, **Then** the system returns a "not found" response (no information leakage).

---

### User Story 3 - Cancel a Pending Order (Priority: P2)

As a customer, I want to cancel an order that has not yet been shipped so that I can change my mind without contacting support.

**Why this priority**: Self-service cancellation reduces support burden and improves customer satisfaction, but it is secondary to the core viewing functionality.

**Independent Test**: Can be fully tested by placing an order, cancelling it before shipment, and verifying the status updates to "cancelled", stock is restored for all items, and the refund is initiated through the payment provider.

**Acceptance Scenarios**:

1. **Given** an order with status "paid", **When** the customer views the order detail, **Then** a "Cancel Order" button is visible.
2. **Given** an order with status "shipped" or "delivered", **When** the customer views the order detail, **Then** no cancel button is shown.
3. **Given** the cancel button is clicked, **When** the confirmation dialog appears and the customer confirms, **Then** the order status changes to "cancelled" and a refund is initiated.
4. **Given** a cancelled order, **When** the refund is processed, **Then** stock quantities for all items in the order are restored.
5. **Given** a cancelled order, **When** the customer views the order in their history, **Then** the status shows as a red "Cancelled" badge.

---

### User Story 4 - Manage Wishlist (Priority: P2)

As a logged-in customer, I want to save products to a wishlist so that I can keep track of items I want to buy later.

**Why this priority**: Wishlist is a valuable engagement feature but is independent of the order management core. It can be implemented and tested without any order-related functionality.

**Independent Test**: Can be fully tested by toggling the wishlist icon on a product page, verifying the product appears on the wishlist page, adding it to cart from the wishlist, and then removing it from the wishlist.

**Acceptance Scenarios**:

1. **Given** a product detail page, **When** the customer clicks the heart/bookmark icon, **Then** the product is added to the wishlist and the icon fills in to indicate "wishlisted".
2. **Given** a product already in the wishlist, **When** the customer clicks the heart icon again, **Then** the product is removed from the wishlist.
3. **Given** the wishlist page, **When** the customer views it, **Then** all wishlisted products are shown with image, name, current price, stock status, "Add to Cart" button, and "Remove" button.
4. **Given** a wishlisted product that goes out of stock, **When** the customer views the wishlist, **Then** the product remains on the list with a clear "Out of Stock" label and the "Add to Cart" button is disabled.
5. **Given** a product already in the wishlist, **When** the customer tries to add it again, **Then** no duplicate is created (the action is silently ignored).
6. **Given** the wishlist page, **When** the customer clicks "Add to Cart" on a product, **Then** the product is added to the cart (using the default variant if variants exist, or prompting variant selection).

---

### User Story 5 - Account Dashboard (Priority: P3)

As a logged-in customer, I want to see a dashboard overview when I access my account so that I can quickly navigate to my orders, addresses, profile, and wishlist.

**Why this priority**: The dashboard is an aggregation view that ties together all account features. It provides the most value when the individual sections (orders, wishlist, addresses, profile) already exist.

**Independent Test**: Can be fully tested by logging in, navigating to the account dashboard, and verifying all summary cards (recent order, saved addresses count, wishlist count, profile completeness) show accurate data and link to the correct sections.

**Acceptance Scenarios**:

1. **Given** a customer with orders, addresses, and wishlist items, **When** they visit the account dashboard, **Then** summary cards display: last order with status, number of saved addresses, wishlist item count, and profile completeness.
2. **Given** the dashboard, **When** the customer clicks a summary card, **Then** they are navigated to the relevant section (orders, addresses, wishlist, or profile).
3. **Given** a desktop viewport, **When** the account area is displayed, **Then** a sidebar navigation shows links to Orders, Addresses, Wishlist, Profile, and Log Out.
4. **Given** a mobile viewport, **When** the account area is displayed, **Then** a tab bar or hamburger menu provides access to the same sections.
5. **Given** the Log Out action, **When** the customer clicks it, **Then** they are logged out and redirected to the homepage.

---

### Edge Cases

- What happens when a customer tries to cancel an order that was already cancelled? The system should show the order is already cancelled and hide the cancel button.
- What happens if the refund fails at the payment provider? The system should mark the refund as failed, keep the order in "cancellation pending" status, and surface the issue for admin resolution.
- What happens if a product on the wishlist is deleted (soft-deleted) by an admin? The product should remain on the wishlist with a "No longer available" label and no "Add to Cart" option.
- What happens if stock is restored from a cancelled order but the product has been soft-deleted? Stock is still restored (the product may be reactivated later), but the product is not re-listed.
- What happens when a customer reorders but some items have changed price? Items are added at the current price, not the historical price. The customer sees current prices in their cart.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST return paginated order history for the authenticated user, sorted newest first.
- **FR-002**: System MUST return full order details including items (with snapshots of product name, variant, price at purchase time), shipping address snapshot, shipping method, and payment summary.
- **FR-003**: System MUST restrict order access — users can only view their own orders. Accessing another user's order returns a "not found" response.
- **FR-004**: System MUST display order status as a color-coded badge: pending (yellow), paid (blue), processing (blue), shipped (purple), delivered (green), cancelled (red), refunded (gray).
- **FR-005**: System MUST allow order cancellation only when order status is "paid" or "processing".
- **FR-006**: System MUST initiate a refund through the payment provider on order cancellation.
- **FR-007**: System MUST restore stock quantities for all items when an order is cancelled.
- **FR-008**: System MUST log all order status changes with timestamp and actor (system or admin) in an order status history.
- **FR-009**: System MUST enforce valid status transitions: pending → paid → processing → shipped → delivered, or pending/paid/processing → cancelled. No other transitions are permitted.
- **FR-010**: System MUST support a "reorder" action that adds all available items from a past order to the current cart at current prices, with warnings for unavailable items.
- **FR-011**: System MUST support a user wishlist with add, remove, and list operations at the product level (not variant level).
- **FR-012**: System MUST prevent duplicate wishlist entries — adding an already-wishlisted product is a no-op.
- **FR-013**: System MUST display a tracking number on the order detail page when available (entered by admin as plain text).
- **FR-014**: System MUST provide an account dashboard showing summary cards for recent order, saved addresses count, wishlist count, and profile completeness.

### Key Entities

- **Order** (extended from Spec 003): Adds status tracking through a defined lifecycle (pending → paid → processing → shipped → delivered or cancelled), tracking number (optional, plain text), and cancellation timestamp.
- **OrderStatusHistory**: A log entry for each status change on an order. Key attributes: order reference, previous status, new status, timestamp, actor (system identifier or admin user reference).
- **WishlistItem**: Links a user to a product at the product level (not variant). Key attributes: user reference, product reference, date added.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find a specific past order within 10 seconds of navigating to the order history page.
- **SC-002**: Order cancellation and refund initiation completes within 5 seconds from user confirmation.
- **SC-003**: Wishlist add/remove actions provide visual feedback within 1 second.
- **SC-004**: Order status changes are reflected in the customer-facing UI within 30 seconds of the status update occurring.
- **SC-005**: 95% of customers who view an order detail page can identify the current order status at a glance (via the status timeline visualization).
- **SC-006**: The reorder action successfully adds items to the cart within 3 seconds, with clear feedback on any unavailable items.

## Assumptions

- Orders are created by the checkout flow in Spec 003. This feature only manages existing orders.
- User authentication and profile/address management are available from Spec 002.
- Product catalog data (images, names, prices, stock) is available from Spec 001.
- Order status transitions beyond "paid" (processing, shipped, delivered) are triggered by admin actions (covered in Spec 005) or external webhook events. This spec only covers the customer-facing display and self-service cancellation.
- Tracking numbers are entered manually by admin as plain text. Integration with shipping carrier APIs is out of scope for v1.
- Email notifications for order status changes are out of scope for v1.
- Refunds are always full refunds of the order total. Partial refunds are out of scope.
- The wishlist is unlimited in size for v1.
- Wishlist operates at the product level, not variant level. When adding a wishlisted product to cart, the customer selects the variant during the add-to-cart flow.
- Profile completeness is defined as having first name, last name, and phone number filled in.

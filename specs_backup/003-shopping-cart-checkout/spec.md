# Feature Specification: Shopping Cart & Checkout

**Feature Branch**: `003-shopping-cart-checkout`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: User description: "Shopping cart and checkout flow — persistent cart, guest cart merge, multi-step checkout with shipping, payment via Stripe, and order confirmation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Products to Cart (Priority: P1)

As a shopper browsing the store, I want to add products (with a selected variant if applicable) to my cart so that I can collect items before purchasing.

**Why this priority**: Adding items to a cart is the foundational action for the entire purchase flow. Without this, no other cart or checkout functionality has value.

**Independent Test**: Can be fully tested by navigating to a product detail page, selecting a variant, clicking "Add to Cart", verifying the cart icon count updates, adding the same product again, and verifying the quantity increments rather than creating a duplicate entry.

**Acceptance Scenarios**:

1. **Given** a product detail page with variants, **When** the shopper selects a variant and clicks "Add to Cart", **Then** the item appears in the cart with quantity 1 and a toast notification confirms the addition with a "View Cart" link.
2. **Given** an item already in the cart, **When** the shopper adds the same product+variant again, **Then** the existing cart item's quantity increments by the added amount (no duplicate line item).
3. **Given** a product that is out of stock, **When** the shopper views the product page, **Then** the "Add to Cart" button is disabled and displays "Out of Stock".
4. **Given** a product with variants, **When** the shopper tries to add to cart without selecting a variant, **Then** the system prompts the shopper to select a variant before proceeding.
5. **Given** any successful add-to-cart action, **When** the toast notification appears, **Then** the cart icon in the header updates to reflect the new total item count.

---

### User Story 2 - View and Edit Cart (Priority: P1)

As a shopper, I want to view my cart with all items, quantities, and prices so that I can review and adjust my selections before checkout.

**Why this priority**: Reviewing and editing the cart is essential before proceeding to checkout. Without this, shoppers cannot verify or correct their selections.

**Independent Test**: Can be fully tested by adding 2 different products, visiting the cart page, changing the quantity of one item, removing the other, and verifying the subtotal and total update correctly.

**Acceptance Scenarios**:

1. **Given** a cart with items, **When** the shopper visits the cart page, **Then** each item is displayed with product image, name, variant details, unit price, quantity selector, line total, and a remove button.
2. **Given** a cart item with quantity 2, **When** the shopper changes the quantity to 3, **Then** the line total and cart summary update immediately.
3. **Given** a cart item, **When** the shopper clicks the remove button, **Then** the item is removed and the cart summary recalculates.
4. **Given** a cart item, **When** the shopper sets the quantity to 0, **Then** the item is removed from the cart.
5. **Given** an empty cart, **When** the shopper visits the cart page, **Then** a friendly message is displayed with a "Continue Shopping" link.
6. **Given** a cart with items, **When** the shopper views the cart summary, **Then** subtotal, estimated tax, and total are displayed correctly.

---

### User Story 3 - Complete Checkout with Shipping and Payment (Priority: P1)

As a shopper ready to buy, I want to go through a multi-step checkout flow (shipping address, shipping method, payment) so that I can complete my purchase securely and receive my order.

**Why this priority**: The checkout flow is the revenue-generating path. It converts cart contents into paid orders and is the core business value of the feature.

**Independent Test**: Can be fully tested by adding items to cart, proceeding to checkout, selecting a saved shipping address (or entering a new one), choosing a shipping method, entering test payment card details, completing the purchase, and verifying the order confirmation page shows all correct details.

**Acceptance Scenarios**:

1. **Given** a shopper with items in the cart, **When** they click "Proceed to Checkout", **Then** they are taken to Step 1 (shipping address) of the checkout flow.
2. **Given** a logged-in user with saved addresses, **When** they reach the shipping address step, **Then** saved addresses appear as selectable cards and one can be picked with a single click.
3. **Given** the shipping address step, **When** the shopper enters a new address and checks "Save to profile", **Then** the address is saved for future use and checkout proceeds.
4. **Given** Step 2 (shipping method), **When** the shopper views available options, **Then** "Standard (5-7 days)" and "Express (2-3 days)" are shown with their prices, and the cheapest option is pre-selected.
5. **Given** a selected shipping method, **When** the shopper views the order summary sidebar, **Then** the shipping cost is included in the total.
6. **Given** Step 3 (payment), **When** the shopper enters valid card details and submits, **Then** payment is processed via Stripe and the shopper advances to the confirmation page.
7. **Given** Step 3 (payment), **When** the payment fails (e.g., declined card), **Then** a clear error message is displayed and the shopper can retry with different details.
8. **Given** an unauthenticated user, **When** they attempt to start checkout, **Then** they are redirected to the login page with a return URL to resume checkout after authentication.

---

### User Story 4 - Order Confirmation (Priority: P2)

As a shopper who has completed payment, I want to see a confirmation page with my order details so that I know my purchase was successful and I have a reference number.

**Why this priority**: While critical for user trust, this is a read-only display that follows the payment step. The core purchase is already complete; this provides the receipt experience.

**Independent Test**: Can be fully tested by completing a full checkout flow and verifying the confirmation page displays the order number, list of purchased items with quantities and prices, shipping address, shipping method, payment summary, and estimated delivery date.

**Acceptance Scenarios**:

1. **Given** a successful payment, **When** the confirmation page loads, **Then** it displays order number, items purchased, shipping address, shipping method, subtotal, shipping cost, tax, and total.
2. **Given** the confirmation page, **When** the shopper looks for next actions, **Then** a "Continue Shopping" button is available that returns to the homepage.
3. **Given** a successful order, **When** the shopper checks their cart, **Then** the cart is empty.
4. **Given** a successful order, **When** the shopper visits their order history, **Then** the new order appears immediately.

---

### User Story 5 - Guest Cart with Merge on Login (Priority: P2)

As a guest visitor, I want to add items to a cart without logging in so that I don't lose my selections if I decide to create an account or log in later.

**Why this priority**: Guest cart improves conversion by removing the friction of requiring login before browsing and collecting items. It is important but depends on the core cart functionality working first.

**Independent Test**: Can be fully tested by adding items as a guest (verifying they persist in the browser), then logging in, and verifying all guest items appear in the authenticated server-side cart with correct quantities.

**Acceptance Scenarios**:

1. **Given** an unauthenticated visitor, **When** they add items to the cart, **Then** the items are stored locally in the browser and the cart functions normally (add, update, remove).
2. **Given** a guest cart with items, **When** the guest logs in or registers, **Then** the guest cart items are merged with any existing server-side cart.
3. **Given** overlapping items in guest and server carts (same product+variant), **When** the merge occurs, **Then** the higher quantity is kept.
4. **Given** a successful merge, **When** the merge completes, **Then** the local browser cart is cleared and the shopper sees only the server-side cart.

---

### Edge Cases

- What happens when a product in the cart goes out of stock before checkout? The system must show which items are affected and prevent checkout until resolved.
- What happens when a product's price changes after it was added to the cart? The cart should reflect the current price, and the shopper should be notified of the change.
- What happens during concurrent checkouts competing for the last unit of stock? The system must use database-level locking to prevent overselling; one checkout succeeds and the other receives an "out of stock" error.
- What happens if the Stripe payment succeeds but the webhook delivery is delayed? The system should also handle client-side payment confirmation as a fallback, then reconcile when the webhook arrives.
- What happens if the shopper navigates away mid-checkout? Their progress (cart contents, selected address/shipping) should be preserved so they can resume.
- What happens if the shopper's session expires during checkout? They should be redirected to login with a return URL that resumes checkout.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain a server-side cart for authenticated users, persisting items across sessions and devices.
- **FR-002**: System MUST support guest carts via browser-local storage with the same add/update/remove operations as the server-side cart.
- **FR-003**: System MUST merge guest cart items with the server-side cart upon login or registration, using the higher quantity for duplicate product+variant combinations.
- **FR-004**: System MUST validate stock availability when adding items to the cart, displaying an appropriate message if the product is out of stock.
- **FR-005**: System MUST re-validate stock availability at checkout time and prevent checkout if any cart item exceeds available stock, clearly indicating which items are affected.
- **FR-006**: System MUST provide a multi-step checkout flow: shipping address, shipping method, payment, and confirmation.
- **FR-007**: System MUST require authentication before checkout. Unauthenticated users are redirected to login with a return URL.
- **FR-008**: System MUST allow shoppers to select a saved address or enter a new address during checkout, with an option to save the new address.
- **FR-009**: System MUST offer at least two shipping options with visible name, estimated delivery window, and cost.
- **FR-010**: System MUST process payments via a PCI-compliant third-party payment provider. Card details must never be transmitted to or stored on our servers.
- **FR-011**: System MUST create an order record only after payment is confirmed as successful.
- **FR-012**: System MUST decrement product/variant stock quantities atomically on successful order placement, preventing race conditions and overselling.
- **FR-013**: System MUST handle payment provider webhook events to update order payment status reliably.
- **FR-014**: System MUST clear the shopper's cart after successful order placement.
- **FR-015**: System MUST display a confirmation page with order number, items, shipping details, and payment summary after successful checkout.
- **FR-016**: System MUST store all monetary values as integer cents internally and display formatted currency to the user.

### Key Entities

- **CartItem**: A product+variant+quantity tuple associated with a user. Ephemeral data that is deleted after order placement. Key attributes: user reference, product reference, variant reference (optional), quantity.
- **Order**: A completed purchase record. Key attributes: human-readable order number, user reference, shipping address (snapshot at time of purchase), shipping method, payment status, order status, subtotal, shipping cost, tax amount, total.
- **OrderItem**: A line item within an order. A snapshot of product name, variant details, unit price, and quantity at the time of purchase. Immutable after creation.
- **Payment**: Tracks the external payment provider reference, amount, currency, status, and timestamps for an order.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A shopper can complete the entire checkout flow (from cart to confirmation) in under 3 minutes.
- **SC-002**: Cart operations (add, update, remove) provide visual feedback within 1 second of the shopper's action.
- **SC-003**: No overselling occurs — stock quantities never go negative, even under concurrent checkout attempts for the same limited-stock item.
- **SC-004**: 99.9% of payment provider events are processed and reflected in order status within 30 seconds of occurrence.
- **SC-005**: 90% of shoppers who begin checkout complete their purchase (measured among those who reach the shipping address step).
- **SC-006**: Guest cart items are fully preserved and correctly merged upon login with zero data loss.

## Assumptions

- Products and variants exist and are managed via the product catalog (Spec 001 dependency).
- User authentication, registration, and saved addresses are available (Spec 002 dependency).
- A third-party payment provider (Stripe) is configured in test mode for development; production keys are managed via environment configuration.
- Tax calculation uses a flat percentage rate (e.g., 21% VAT) in v1. Integration with real-time tax calculation services is out of scope.
- Shipping options and prices are fixed/hardcoded in v1. Dynamic shipping rate calculation is out of scope.
- Free shipping above a certain order value is included: orders over a configured threshold (e.g., 100 currency units) qualify for free standard shipping.
- Promo codes, coupons, and discount logic are out of scope for v1.
- Only card payments are supported in v1. Alternative payment methods (PayPal, Apple Pay, etc.) are out of scope.
- Multi-currency support is out of scope — single currency only.
- Saved payment methods / wallet functionality is out of scope for v1.
- Order editing after placement is out of scope.
- Subscription / recurring orders are out of scope.

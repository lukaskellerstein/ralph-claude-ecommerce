# Feature Specification: Shopping Cart & Checkout

| Field          | Value                          |
|----------------|--------------------------------|
| Feature Branch | 003-shopping-cart-checkout     |
| Created        | 2026-04-14                     |
| Status         | Draft                          |

## 1. Overview

The shopping cart and checkout flow is the revenue-critical path of the application. It allows customers to add products to a persistent cart, review their selections, enter shipping and payment information, and complete a purchase. The cart is server-side for logged-in users and merges with any guest cart on login.

## 2. User Stories

### US-001: Add Products to Cart

**As a** shopper,
**I want to** add products (with selected variant) to my cart,
**So that** I can collect items before purchasing.

**Acceptance Criteria:**

- "Add to Cart" button is on the product detail page and optionally on product cards in listings.
- If the product has variants, a variant MUST be selected before adding to cart.
- Adding a product that is already in the cart increments its quantity (does not create a duplicate).
- A toast notification confirms the addition with the product name and a "View Cart" link.
- Cart icon in the header updates to show the total item count.
- If the product is out of stock, the "Add to Cart" button is disabled with an "Out of Stock" label.
- Cart API: `POST /api/v1/cart/items` with `{ product_id, variant_id?, quantity }`.

**Independent Test:** Can be fully tested by adding a product to the cart from the product page, verifying the cart count updates, adding the same product again and verifying the quantity increments.

### US-002: View and Edit Cart

**As a** shopper,
**I want to** view my cart with all items, quantities, and prices,
**So that** I can review and adjust my selections before checkout.

**Acceptance Criteria:**

- Cart page (`/cart`) shows a list of all cart items with: product image, name, variant details, unit price, quantity selector, line total, and a remove button.
- Quantity can be adjusted between 1 and available stock via a number input or +/- buttons.
- If quantity is set to 0 or the remove button is clicked, the item is removed from the cart.
- Cart summary shows: subtotal, estimated tax (if applicable), and a total.
- A "Proceed to Checkout" button navigates to the checkout flow.
- An empty cart shows a friendly message with a "Continue Shopping" link.
- Cart API: `GET /api/v1/cart`, `PATCH /api/v1/cart/items/:id`, `DELETE /api/v1/cart/items/:id`.

**Independent Test:** Can be fully tested by adding 2 different products, visiting the cart page, changing quantity of one, removing the other, and verifying the totals update correctly.

### US-003: Guest Cart with Merge on Login

**As a** guest visitor,
**I want to** add items to a cart without logging in,
**So that** I don't lose my selections if I decide to create an account or log in later.

**Acceptance Criteria:**

- Guest carts are stored in localStorage on the frontend with the same data structure as server carts.
- When a guest logs in or registers, the guest cart items are sent to the server and merged with any existing server cart.
- Merge strategy: if the same product+variant exists in both, keep the higher quantity.
- After merge, the localStorage cart is cleared.
- Guest cart supports the same add/update/remove operations as the authenticated cart (all client-side).

**Independent Test:** Can be fully tested by adding items as a guest, logging in, and verifying all guest items appear in the authenticated cart with correct quantities.

### US-004: Checkout — Enter Shipping Address

**As a** shopper ready to buy,
**I want to** enter or select a shipping address during checkout,
**So that** my order is delivered to the right location.

**Acceptance Criteria:**

- Checkout is a multi-step flow. Step 1 is the shipping address.
- If the user has saved addresses, they are shown as selectable cards. One can be picked with a single click.
- User can also enter a new address inline (same fields as the address form in spec 002).
- A checkbox allows saving the new address to the user's profile.
- "Continue" button advances to the next step only if a valid address is provided.
- Checkout requires authentication — unauthenticated users are redirected to login (with a return URL).

**Independent Test:** Can be fully tested by starting checkout with a saved address, selecting it, and advancing; then starting again and entering a new address.

### US-005: Checkout — Select Shipping Method

**As a** shopper,
**I want to** choose a shipping method,
**So that** I can balance delivery speed with cost.

**Acceptance Criteria:**

- Step 2 of checkout presents available shipping options.
- Options for v1 are hardcoded: "Standard (5-7 days)" and "Express (2-3 days)" with fixed prices.
- Each option shows the name, estimated delivery window, and cost.
- Selected shipping cost is added to the order total visible in the sidebar summary.
- Default selection is the cheapest option.

[NEEDS CLARIFICATION: Should shipping be free above a certain order value in v1?]

**Independent Test:** Can be fully tested by selecting each shipping option and verifying the order total updates correctly.

### US-006: Checkout — Payment via Stripe

**As a** shopper,
**I want to** enter my payment details securely,
**So that** I can pay for my order.

**Acceptance Criteria:**

- Step 3 of checkout shows a Stripe Elements card input (card number, expiry, CVC).
- Payment is processed via Stripe Payment Intents API — card details NEVER touch our server.
- The backend creates a PaymentIntent with the order total and returns the `client_secret` to the frontend.
- On successful payment confirmation, the frontend advances to the confirmation step.
- On payment failure, a clear error message is displayed and the user can retry.
- The order is only created in our database after Stripe confirms payment success (via webhook or client confirmation).

**Independent Test:** Can be fully tested using Stripe test card numbers (e.g., 4242 4242 4242 4242) in test mode, verifying successful payment and order creation, then using a declining card and verifying the error state.

### US-007: Checkout — Order Confirmation

**As a** shopper who has completed payment,
**I want to** see a confirmation page with my order details,
**So that** I know my purchase was successful and have a reference number.

**Acceptance Criteria:**

- Confirmation page shows: order number, list of purchased items with quantities and prices, shipping address, shipping method, payment summary (subtotal, shipping, tax, total), and estimated delivery date.
- A "Continue Shopping" button returns the user to the homepage.
- The user's cart is cleared after successful order placement.
- The order appears immediately in the user's order history (spec 004).

**Independent Test:** Can be fully tested by completing a full checkout flow and verifying all order details on the confirmation page match what was entered.

## 3. Functional Requirements

- **FR-001:** System MUST maintain a server-side cart for authenticated users in a `cart_items` table.
- **FR-002:** System MUST support guest carts via frontend localStorage with merge on authentication.
- **FR-003:** System MUST validate stock availability before adding to cart and at checkout time.
- **FR-004:** System MUST prevent checkout if any cart item is out of stock — show which items are affected.
- **FR-005:** System MUST create a Stripe PaymentIntent via `POST /api/v1/checkout/payment-intent` with the order total.
- **FR-006:** System MUST handle Stripe webhook events (`payment_intent.succeeded`, `payment_intent.payment_failed`) to update order status.
- **FR-007:** System MUST create an order record with status `pending` before payment, update to `paid` on success.
- **FR-008:** System MUST decrement product/variant stock quantities on successful order placement.
- **FR-009:** System MUST prevent race conditions on stock decrement (use database-level locking or atomic operations).
- **FR-010:** System MUST clear the user's cart after successful order placement.
- **FR-011:** Checkout flow endpoint: `POST /api/v1/checkout` creates the order from the current cart + shipping details.

## 4. Core Entities (What, Not How)

- **CartItem:** A product+variant+quantity tuple associated with a user. Ephemeral — deleted after order placement.
- **Order:** A completed purchase. Key attributes: order number (human-readable), user, shipping address (snapshot), shipping method, payment status, order status, totals.
- **OrderItem:** A line item within an order. Snapshot of product name, price, variant, and quantity at time of purchase.
- **Payment:** Tracks the Stripe PaymentIntent ID, amount, status, and timestamps for an order.

## 5. Success Criteria

- **SC-001:** A user can complete checkout (cart to confirmation) in under 3 minutes.
- **SC-002:** Cart operations (add, update, remove) respond in under 200ms.
- **SC-003:** No overselling — stock quantity is never negative after concurrent checkouts.
- **SC-004:** 99.9% of Stripe webhook events are processed successfully.

## 6. Assumptions and Dependencies

- **Depends on:** Spec 001 (products exist to add to cart), Spec 002 (user is authenticated for checkout, addresses available).
- Stripe account is configured in test mode for development.
- Tax calculation is a flat percentage in v1 (e.g., 21% VAT). Real tax calculation services are out of scope.
- Promo codes / discounts are out of scope for v1.
- Multi-currency is out of scope — single currency only.

## 7. Out of Scope

- Promo codes, coupons, and discount logic.
- Saved payment methods / wallet.
- PayPal, Apple Pay, or other non-card payment methods.
- Order editing after placement.
- Real-time tax calculation via third-party service.
- Subscription / recurring orders.

## 8. Review & Acceptance Checklist

- [ ] All user stories have clear acceptance criteria
- [ ] Functional requirements are testable and unambiguous
- [ ] No implementation details leaked into the spec (tech-agnostic "what")
- [ ] All ambiguities marked with [NEEDS CLARIFICATION]
- [ ] Success criteria are measurable
- [ ] Out of scope items are explicitly listed
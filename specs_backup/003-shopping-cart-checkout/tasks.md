# Tasks: Shopping Cart & Checkout

**Input**: Design documents from `/specs/003-shopping-cart-checkout/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cart.md, contracts/checkout.md, quickstart.md

**Tests**: Included per Constitution Principle IV (testing standards mandate integration tests for every API endpoint, component tests for every React page, and e2e tests for critical flows including checkout).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies, extend configuration, prepare Stripe integration

- [ ] T001 Add `stripe` dependency to `backend/requirements.txt` (or `pyproject.toml`)
- [ ] T002 [P] Add `@stripe/stripe-js` and `@stripe/react-stripe-js` dependencies to `frontend/package.json`
- [ ] T003 [P] Extend backend config with Stripe, shipping, and tax settings in `backend/app/core/config.py` — add `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`, `FREE_SHIPPING_THRESHOLD`, `STANDARD_SHIPPING_COST`, `EXPRESS_SHIPPING_COST`, `TAX_RATE`, `CURRENCY`
- [ ] T004 [P] Update `.env.example` with all new environment variables (Stripe keys, shipping costs, tax rate, currency)
- [ ] T005 [P] Create Stripe.js initialization utility in `frontend/src/lib/stripe.ts` — export `loadStripe(publishableKey)` singleton

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models, migrations, and shared services that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create CartItem SQLAlchemy model in `backend/app/models/cart.py` — UUID PK, user_id FK, product_id FK, variant_id FK (nullable), quantity, created_at, updated_at. Unique constraint on (user_id, product_id, variant_id). Hard delete behavior.
- [ ] T007 [P] Create Order SQLAlchemy model in `backend/app/models/order.py` — UUID PK, order_number (unique), user_id FK, status, payment_status, shipping_address (JSONB), shipping_method, shipping_cost, subtotal, tax_amount, total, estimated_delivery_date, deleted_at (soft delete), created_at, updated_at. CHECK constraints on status and payment_status.
- [ ] T008 [P] Create OrderItem SQLAlchemy model in `backend/app/models/order.py` — UUID PK, order_id FK (CASCADE), product_id FK, variant_id FK (nullable), product_name, variant_type, variant_value, sku, unit_price, quantity, line_total, created_at, updated_at.
- [ ] T009 [P] Create Payment SQLAlchemy model in `backend/app/models/order.py` — UUID PK, order_id FK (unique), stripe_payment_intent_id (unique), amount, currency, status, stripe_client_secret, paid_at, failed_at, created_at, updated_at.
- [ ] T010 [P] Create OrderCounter SQLAlchemy model in `backend/app/models/order.py` — date PK, counter INTEGER for human-readable order number generation.
- [ ] T011 Create Alembic migration for cart_items, orders, order_items, payments, order_counters tables in `backend/alembic/versions/xxxx_add_cart_order_tables.py` — run `alembic revision --autogenerate` and verify indexes on all FKs and query columns (depends on T006-T010)
- [ ] T012 [P] Create Pydantic request/response schemas for cart in `backend/app/schemas/cart.py` — CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse, CartMergeRequest per contracts/cart.md
- [ ] T013 [P] Create Pydantic request/response schemas for orders/checkout in `backend/app/schemas/order.py` — CheckoutRequest, CheckoutResponse, OrderResponse, OrderListResponse, OrderDetailResponse, PaymentConfirmRequest, StripeWebhookEvent per contracts/checkout.md
- [ ] T014 [P] Create Stripe service in `backend/app/services/stripe_service.py` — `create_payment_intent(amount, currency, metadata)`, `verify_webhook_signature(payload, sig_header)`, `retrieve_payment_intent(pi_id)`. Wraps Stripe SDK calls.
- [ ] T015 Register cart, checkout, and webhook routers in `backend/app/main.py` — import and include routers with `/api/v1` prefix

**Checkpoint**: Foundation ready — all models, schemas, and shared services in place. User story implementation can begin.

---

## Phase 3: User Story 1 — Add Products to Cart (Priority: P1) MVP

**Goal**: Shoppers can add products to a server-side cart. Adding duplicates increments quantity. Out-of-stock products are blocked. Cart icon shows item count.

**Independent Test**: Add a product from the product page, verify cart count updates, add same product again, verify quantity increments.

### Tests for User Story 1

- [ ] T016 [P] [US1] Integration test for POST /api/v1/cart/items in `backend/tests/test_cart.py` — test add new item, add duplicate (quantity increment), add out-of-stock item (400), add product requiring variant without variant_id (400), add nonexistent product (404)
- [ ] T017 [P] [US1] Component test for add-to-cart interaction on product detail page in `frontend/tests/cart.test.tsx` — test button click triggers API call, toast notification appears, cart count updates in header

### Implementation for User Story 1

- [ ] T018 [US1] Implement cart_service.add_item in `backend/app/services/cart_service.py` — validate product exists and is active, validate variant if product has variants, check stock availability, upsert cart item (increment quantity if exists), return updated cart
- [ ] T019 [US1] Implement POST /api/v1/cart/items endpoint in `backend/app/api/v1/cart.py` — auth required, validate request body, call cart_service.add_item, return full cart response with item details and subtotal
- [ ] T020 [P] [US1] Create use-cart TanStack Query hook in `frontend/src/hooks/use-cart.ts` — `useAddToCart` mutation hook that POSTs to /api/v1/cart/items and invalidates cart query cache
- [ ] T021 [US1] Add "Add to Cart" button to product detail page in `frontend/src/pages/product-detail.tsx` — variant must be selected first (if applicable), disabled when out of stock with "Out of Stock" label, on success show toast with product name and "View Cart" link
- [ ] T022 [US1] Add cart icon with item count badge to header in `frontend/src/components/user-menu.tsx` (or header component) — reads from cart query, updates reactively on add

**Checkpoint**: User Story 1 complete — adding products to cart works end-to-end.

---

## Phase 4: User Story 2 — View and Edit Cart (Priority: P1)

**Goal**: Shoppers can view all cart items, change quantities, remove items, see totals, and proceed to checkout.

**Independent Test**: Add 2 products, visit /cart, change quantity of one, remove the other, verify totals recalculate correctly.

### Tests for User Story 2

- [ ] T023 [P] [US2] Integration tests for GET/PATCH/DELETE cart endpoints in `backend/tests/test_cart.py` — test GET returns all items with product details, PATCH updates quantity (check stock limit), PATCH with quantity exceeding stock (400), DELETE removes item, verify subtotal recalculation
- [ ] T024 [P] [US2] Component test for cart page in `frontend/tests/cart.test.tsx` — test items render with images/names/prices, quantity change updates totals, remove button removes item, empty cart shows message with "Continue Shopping" link

### Implementation for User Story 2

- [ ] T025 [US2] Implement cart_service.get_cart in `backend/app/services/cart_service.py` — return all cart items for user with joined product, variant, and primary image data; compute unit_price (variant price_override or base_price), line_total, subtotal, item_count
- [ ] T026 [US2] Implement cart_service.update_item and cart_service.remove_item in `backend/app/services/cart_service.py` — update validates quantity > 0 and stock availability, remove hard-deletes the cart item; both return updated cart
- [ ] T027 [US2] Implement GET /api/v1/cart, PATCH /api/v1/cart/items/{item_id}, DELETE /api/v1/cart/items/{item_id} endpoints in `backend/app/api/v1/cart.py` — all auth required, verify item belongs to current user
- [ ] T028 [P] [US2] Extend use-cart hook in `frontend/src/hooks/use-cart.ts` — add `useCart` query hook (GET), `useUpdateCartItem` mutation (PATCH), `useRemoveCartItem` mutation (DELETE); invalidate cache on mutations
- [ ] T029 [P] [US2] Create cart item row component in `frontend/src/components/cart-item.tsx` — product image, name, variant details, unit price, quantity selector (+/- buttons or number input, min 1, max stock), line total, remove button
- [ ] T030 [P] [US2] Create cart summary component in `frontend/src/components/cart-summary.tsx` — subtotal, estimated tax (subtotal * TAX_RATE), total, "Proceed to Checkout" button
- [ ] T031 [US2] Create cart page in `frontend/src/pages/cart.tsx` — list of cart-item components, cart-summary sidebar, empty state with "Continue Shopping" link; add `/cart` route to `frontend/src/App.tsx`
- [ ] T032 [US2] Add zod validation schemas for cart operations in `frontend/src/lib/validations.ts` — quantity validation (integer, min 1)
- [ ] T033 [US2] Add Cart, CartItem, CartResponse types to `frontend/src/lib/types.ts`

**Checkpoint**: User Stories 1 & 2 complete — full cart CRUD works end-to-end with UI.

---

## Phase 5: User Story 3 — Complete Checkout with Shipping and Payment (Priority: P1)

**Goal**: Authenticated shoppers go through a multi-step checkout: select/enter shipping address, choose shipping method, pay via Stripe, and have an order created.

**Independent Test**: Add items, proceed to checkout, select saved address, choose shipping, enter Stripe test card (4242...), complete payment, verify order is created with correct totals.

### Tests for User Story 3

- [ ] T034 [P] [US3] Integration test for POST /api/v1/checkout in `backend/tests/test_checkout.py` — test with saved address, test with new address (+ save_address flag), test with empty cart (400), test with out-of-stock item (400 with affected_items), test unauthenticated (401), verify order record created with status pending, verify PaymentIntent created with correct amount
- [ ] T035 [P] [US3] Integration test for POST /api/v1/checkout/confirm in `backend/tests/test_checkout.py` — test successful confirmation updates order to paid, test mismatched payment_intent_id (400), test order not found (404)
- [ ] T036 [P] [US3] Integration test for POST /api/v1/webhooks/stripe in `backend/tests/test_webhooks.py` — test payment_intent.succeeded updates order status + decrements stock + clears cart, test payment_intent.payment_failed cancels order, test invalid signature (400), test idempotent reprocessing (already paid order)
- [ ] T037 [P] [US3] Component test for checkout page in `frontend/tests/checkout.test.tsx` — test step navigation (address → shipping → payment), test saved address selection, test new address form validation, test shipping method selection updates total, test Stripe Elements renders

### Implementation for User Story 3

- [ ] T038 [US3] Implement checkout_service.create_order in `backend/app/services/checkout_service.py` — validate cart not empty, validate stock for all items (SELECT FOR UPDATE), resolve shipping address (saved or new, optionally save), calculate subtotal/shipping/tax/total, generate order number (OrderCounter), create Order + OrderItems, create PaymentIntent via stripe_service, create Payment record, return order + client_secret
- [ ] T039 [US3] Implement checkout_service.confirm_payment in `backend/app/services/checkout_service.py` — verify order belongs to user, verify payment_intent_id matches, check PaymentIntent status with Stripe, if succeeded: update order to paid, decrement stock atomically (FOR UPDATE), clear cart
- [ ] T040 [US3] Implement checkout_service.handle_webhook in `backend/app/services/checkout_service.py` — for payment_intent.succeeded: idempotently update order to paid, decrement stock, clear cart; for payment_intent.payment_failed: update order to cancelled
- [ ] T041 [US3] Implement order number generation in `backend/app/services/checkout_service.py` — INSERT INTO order_counters ON CONFLICT (date) DO UPDATE SET counter = counter + 1 RETURNING counter; format as ORD-YYYYMMDD-NNNNN
- [ ] T042 [US3] Implement POST /api/v1/checkout endpoint in `backend/app/api/v1/checkout.py` — auth required, validate CheckoutRequest, call checkout_service.create_order, return 201 with order + payment client_secret
- [ ] T043 [US3] Implement POST /api/v1/checkout/confirm endpoint in `backend/app/api/v1/checkout.py` — auth required, call checkout_service.confirm_payment
- [ ] T044 [US3] Implement POST /api/v1/webhooks/stripe endpoint in `backend/app/api/v1/webhooks.py` — no auth, verify signature via stripe_service, parse event, call checkout_service.handle_webhook, return 200
- [ ] T045 [P] [US3] Create checkout step indicator component in `frontend/src/components/checkout-steps.tsx` — visual stepper showing current step (address, shipping, payment, confirmation) with completed/active/upcoming states
- [ ] T046 [P] [US3] Create shipping address step component in `frontend/src/components/shipping-address-step.tsx` — show saved addresses as selectable cards, inline new address form (reuse address-form from spec 002), "Save to profile" checkbox, "Continue" button validates address
- [ ] T047 [P] [US3] Create shipping method step component in `frontend/src/components/shipping-method-step.tsx` — radio cards for Standard (5-7 days) and Express (2-3 days) with prices, cheapest pre-selected, show "Free" badge when subtotal exceeds threshold
- [ ] T048 [P] [US3] Create payment step component in `frontend/src/components/payment-step.tsx` — Stripe Elements CardElement, wrapped in Elements provider with client_secret, handle confirmCardPayment, show error on failure with retry option
- [ ] T049 [P] [US3] Create order summary sidebar component in `frontend/src/components/order-summary-sidebar.tsx` — show cart items (compact), subtotal, shipping cost, tax, total; updates as shipping method changes
- [ ] T050 [US3] Create use-checkout hook in `frontend/src/hooks/use-checkout.ts` — `useCreateOrder` mutation (POST /checkout), `useConfirmPayment` mutation (POST /checkout/confirm)
- [ ] T051 [US3] Create checkout page in `frontend/src/pages/checkout.tsx` — multi-step form with step state management, wraps payment step in Stripe Elements provider, redirects unauthenticated users to login with returnUrl; add `/checkout` as protected route in `frontend/src/App.tsx`
- [ ] T052 [US3] Add zod validation schemas for checkout forms in `frontend/src/lib/validations.ts` — shipping address schema, shipping method enum, payment confirmation schema
- [ ] T053 [US3] Add Order, OrderItem, Payment, CheckoutRequest, CheckoutResponse types to `frontend/src/lib/types.ts`

**Checkpoint**: User Story 3 complete — full checkout flow works end-to-end including Stripe test payments.

---

## Phase 6: User Story 4 — Order Confirmation (Priority: P2)

**Goal**: After successful payment, shoppers see a confirmation page with order number, items, shipping details, and payment summary. Cart is cleared.

**Independent Test**: Complete checkout, verify confirmation page shows order number, all items, correct totals, shipping address, and estimated delivery. Verify cart is empty. Verify order appears in order history.

### Tests for User Story 4

- [ ] T054 [P] [US4] Integration tests for GET /api/v1/orders and GET /api/v1/orders/{order_id} in `backend/tests/test_checkout.py` — test order list with pagination, test order detail returns full data, test other user cannot access (404), test unauthenticated (401)
- [ ] T055 [P] [US4] Component test for order confirmation page in `frontend/tests/order-confirmation.test.tsx` — test all order details render correctly, test "Continue Shopping" button links to homepage

### Implementation for User Story 4

- [ ] T056 [US4] Implement order_service.get_orders and order_service.get_order_detail in `backend/app/services/checkout_service.py` — get_orders: cursor-based paginated list for user (soft-delete filtered), returns summary (order_number, status, item_count, total, date); get_order_detail: full order with items, address, payment info, verify ownership
- [ ] T057 [US4] Implement GET /api/v1/orders and GET /api/v1/orders/{order_id} endpoints in `backend/app/api/v1/checkout.py` — auth required, cursor-based pagination for list, ownership check for detail
- [ ] T058 [P] [US4] Create use-orders hook in `frontend/src/hooks/use-orders.ts` — `useOrders` paginated query (GET /orders), `useOrder` query by ID (GET /orders/:id)
- [ ] T059 [US4] Create order confirmation page in `frontend/src/pages/order-confirmation.tsx` — display order number, item list with quantities and prices, shipping address, shipping method, subtotal/shipping/tax/total, estimated delivery date, "Continue Shopping" button; add `/orders/:orderId/confirmation` as protected route in `frontend/src/App.tsx`
- [ ] T060 [US4] Wire checkout success to confirmation page — after successful payment confirmation in checkout.tsx, redirect to `/orders/:orderId/confirmation`

**Checkpoint**: User Stories 1-4 complete — full shopping flow from add-to-cart through order confirmation.

---

## Phase 7: User Story 5 — Guest Cart with Merge on Login (Priority: P2)

**Goal**: Guest visitors can add items to a localStorage cart. On login/register, guest cart merges with server cart using higher-quantity strategy.

**Independent Test**: Add items as guest (verify localStorage), log in, verify all guest items appear in server cart with correct quantities.

### Tests for User Story 5

- [ ] T061 [P] [US5] Integration test for POST /api/v1/cart/merge in `backend/tests/test_cart.py` — test merge with no server cart (all items added), test merge with overlapping items (higher quantity wins), test merge with inactive/out-of-stock items (silently skipped), test empty merge request
- [ ] T062 [P] [US5] Component test for guest cart behavior in `frontend/tests/cart.test.tsx` — test localStorage add/update/remove, test merge triggered on login, test localStorage cleared after merge

### Implementation for User Story 5

- [ ] T063 [US5] Implement cart_service.merge_guest_cart in `backend/app/services/cart_service.py` — accept list of {product_id, variant_id, quantity}, for each: validate product/variant active and in stock, if same item in server cart keep MAX(quantities), else add item; return merged cart
- [ ] T064 [US5] Implement POST /api/v1/cart/merge endpoint in `backend/app/api/v1/cart.py` — auth required, validate CartMergeRequest body, call cart_service.merge_guest_cart, return full cart
- [ ] T065 [US5] Create guest cart localStorage utilities in `frontend/src/lib/guest-cart.ts` — `getGuestCart()`, `addGuestCartItem(productId, variantId, quantity)`, `updateGuestCartItem(productId, variantId, quantity)`, `removeGuestCartItem(productId, variantId)`, `clearGuestCart()`, `getGuestCartCount()`
- [ ] T066 [US5] Integrate guest cart with cart hooks in `frontend/src/hooks/use-cart.ts` — when unauthenticated, use guest-cart utilities instead of API calls; `useCart` returns localStorage items for guests
- [ ] T067 [US5] Trigger merge on login/register in `frontend/src/hooks/use-auth.ts` — after successful login/register, if guest cart has items, call POST /api/v1/cart/merge then clearGuestCart()
- [ ] T068 [US5] Update cart page in `frontend/src/pages/cart.tsx` — works for both guest (localStorage) and authenticated (API) users; guest cart shows "Log in to checkout" instead of "Proceed to Checkout"

**Checkpoint**: All 5 user stories complete — full cart and checkout experience for both guests and authenticated users.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end tests, security hardening, performance validation

- [ ] T069 [P] End-to-end test for complete checkout flow (guest → login → cart → checkout → confirmation) in `frontend/tests/e2e/checkout.test.tsx` or equivalent e2e framework
- [ ] T070 [P] End-to-end test for stock exhaustion scenario (concurrent checkouts for last item) in `backend/tests/test_checkout.py`
- [ ] T071 [P] Verify Stripe webhook signature validation rejects invalid signatures in `backend/tests/test_webhooks.py`
- [ ] T072 [P] Add rate limiting to checkout endpoint if not already covered by global rate limiting in `backend/app/api/v1/checkout.py`
- [ ] T073 Run quickstart.md validation — verify all setup steps work, test cards produce expected results, Stripe CLI webhook forwarding works
- [ ] T074 Verify all monetary values stored as integer cents — audit Order, OrderItem, Payment models and all API responses
- [ ] T075 Verify cart price change detection — if a product price changes after being added to cart, cart reflects current price

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2)
- **US2 (Phase 4)**: Depends on US1 (Phase 3) — needs add-to-cart to have items to view/edit
- **US3 (Phase 5)**: Depends on US2 (Phase 4) — needs a functional cart to checkout from
- **US4 (Phase 6)**: Depends on US3 (Phase 5) — needs a completed order to show confirmation
- **US5 (Phase 7)**: Depends on US2 (Phase 4) — needs cart API working, independent from US3/US4
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1: Setup
  ↓
Phase 2: Foundational
  ↓
Phase 3: US1 (Add to Cart)
  ↓
Phase 4: US2 (View/Edit Cart)
  ↓ ↘
Phase 5: US3 (Checkout)    Phase 7: US5 (Guest Cart) ← can run in parallel with US3
  ↓
Phase 6: US4 (Confirmation)
  ↓
Phase 8: Polish
```

### Within Each User Story

- Tests written first (they will fail until implementation)
- Backend models/services before API endpoints
- API endpoints before frontend hooks
- Frontend hooks before page components
- Page components integrate everything

### Parallel Opportunities

- **Phase 1**: T002, T003, T004, T005 can all run in parallel
- **Phase 2**: T007-T010 (models) can run in parallel, T012-T014 can run in parallel after models
- **Phase 3**: T016+T017 (tests) in parallel; T020 (hook) in parallel with backend work
- **Phase 4**: T023+T024 (tests) in parallel; T028+T029+T030 (frontend) in parallel
- **Phase 5**: T034-T037 (tests) in parallel; T045-T049 (frontend components) all in parallel
- **Phase 6**: T054+T055 (tests) in parallel; T058 (hook) in parallel with backend
- **Phase 7**: T061+T062 (tests) in parallel
- **US3 and US5 can run in parallel** after US2 completes

---

## Parallel Example: User Story 3 (Checkout)

```bash
# Launch all tests in parallel:
T034: Integration test for POST /api/v1/checkout
T035: Integration test for POST /api/v1/checkout/confirm
T036: Integration test for POST /api/v1/webhooks/stripe
T037: Component test for checkout page

# Launch all frontend components in parallel:
T045: Checkout step indicator
T046: Shipping address step
T047: Shipping method step
T048: Payment step (Stripe Elements)
T049: Order summary sidebar
```

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1 — Add to Cart
4. Complete Phase 4: US2 — View and Edit Cart
5. Complete Phase 5: US3 — Checkout with Payment
6. **STOP and VALIDATE**: Full purchase flow works end-to-end with Stripe test cards
7. Deploy/demo if ready — this is a functional ecommerce checkout

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 + US2 → Cart fully functional (can demo cart experience)
3. US3 → Checkout works (MVP! Can take payments)
4. US4 → Confirmation page (better UX post-purchase)
5. US5 → Guest cart (improved conversion for non-logged-in visitors)
6. Polish → E2e tests, security hardening, edge cases

### Parallel Team Strategy

With multiple developers after Foundational phase:
- **Developer A**: US1 → US2 (cart backend + frontend)
- **Developer B**: US3 backend (checkout service, Stripe, webhooks) — starts after US1 backend is done
- **Developer C**: US5 (guest cart) — starts after US2 is done
- Then: Developer A takes US4, Developer B does US3 frontend, Developer C does Polish

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- All Stripe operations use test mode — see quickstart.md for test card numbers
- Stock decrement uses SELECT FOR UPDATE — see research.md R-002
- Order numbers use date-partitioned counter — see research.md R-005
- Webhook endpoint has no auth (verified by Stripe signature) — see research.md R-004
- Tax is flat rate (21% default) — see research.md R-007
- Free standard shipping above 10000 cents — see research.md R-006

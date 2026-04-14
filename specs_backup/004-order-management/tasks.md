# Tasks: Order Management & User Account

**Input**: Design documents from `/specs/004-order-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/orders.md, contracts/wishlist.md, contracts/account.md, quickstart.md

**Tests**: Included per Constitution Principle IV (testing standards mandate integration tests for every API endpoint, component tests for every React page, and e2e tests for critical flows including cancellation).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new dependencies needed. Extend existing configuration and models for order management.

- [ ] T001 Extend Order model with `tracking_number` (VARCHAR(100), nullable) and `cancelled_at` (TIMESTAMP, nullable) columns in `backend/app/models/order.py` — also add `processing` to the status CHECK constraint
- [ ] T002 [P] Create OrderStatusHistory SQLAlchemy model in `backend/app/models/order_status.py` — UUID PK, order_id FK (CASCADE), previous_status (nullable), new_status, actor_type CHECK ('system','customer','admin'), actor_id (nullable UUID), note (nullable TEXT), created_at. Indexes on order_id, (order_id, created_at), new_status.
- [ ] T003 [P] Create WishlistItem SQLAlchemy model in `backend/app/models/wishlist.py` — UUID PK, user_id FK (CASCADE), product_id FK, created_at. Unique constraint on (user_id, product_id). Hard delete behavior.
- [ ] T004 Create Alembic migration for order extensions, order_status_history, and wishlist_items tables in `backend/alembic/versions/xxxx_add_order_status_history_wishlist.py` — run `alembic revision --autogenerate` (depends on T001-T003)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schemas, services, and status machine that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Define order status transition state machine in `backend/app/services/order_service.py` — implement VALID_TRANSITIONS dict, `validate_transition(current_status, new_status)` function, and `log_status_change(order_id, prev_status, new_status, actor_type, actor_id, note)` that creates an OrderStatusHistory record
- [ ] T006 [P] Create/extend Pydantic schemas for order management in `backend/app/schemas/order.py` — add OrderDetailResponse (with status_history, can_cancel, tracking_number), OrderCancelRequest (reason optional), OrderCancelResponse (with refund_status), ReorderResponse (added_items, unavailable_items), OrderStatusHistoryResponse, StatusBadge mapping
- [ ] T007 [P] Create Pydantic schemas for wishlist in `backend/app/schemas/wishlist.py` — WishlistItemResponse (with product details), WishlistAddRequest, WishlistCheckRequest, WishlistCheckResponse
- [ ] T008 [P] Create Pydantic schema for account dashboard in `backend/app/schemas/account.py` — DashboardResponse (recent_order, address_count, wishlist_count, profile_complete)
- [ ] T009 [P] Create Stripe refund service in `backend/app/services/refund_service.py` — `create_refund(payment_intent_id)` wrapping `stripe.Refund.create()`, returns refund status
- [ ] T010 Register orders, wishlist, and account routers in `backend/app/main.py` — import and include with `/api/v1` prefix
- [ ] T011 [P] Add OrderStatusHistory, WishlistItem, DashboardData, ReorderResult types to `frontend/src/lib/types.ts`
- [ ] T012 [P] Add cancel reason zod schema to `frontend/src/lib/validations.ts`

**Checkpoint**: Foundation ready — models, schemas, state machine, and refund service in place.

---

## Phase 3: User Story 1 — View Order History (Priority: P1) MVP

**Goal**: Customers can see a paginated list of all their orders with status badges, sorted newest first.

**Independent Test**: Place 2+ orders, navigate to order history, verify all orders appear in correct order with accurate details and color-coded status badges.

### Tests for User Story 1

- [ ] T013 [P] [US1] Integration test for GET /api/v1/orders in `backend/tests/test_orders.py` — test paginated list (10 per page), test ordering (newest first), test status filter, test empty state, test unauthenticated (401), test user can only see own orders
- [ ] T014 [P] [US1] Component test for order history page in `frontend/tests/order-history.test.tsx` — test orders render with order number, date, item count, total, status badge; test pagination ("Load More"); test empty state with "Start Shopping" link

### Implementation for User Story 1

- [ ] T015 [US1] Implement order_service.list_orders in `backend/app/services/order_service.py` — cursor-based paginated query filtered by user_id, optional status filter, ordered by created_at DESC, soft-delete filtered, returns order summaries (order_number, status, item_count, total, date)
- [ ] T016 [US1] Implement GET /api/v1/orders endpoint in `backend/app/api/v1/orders.py` — auth required, call order_service.list_orders, return paginated response with cursor
- [ ] T017 [P] [US1] Create order status badge component in `frontend/src/components/order-status-badge.tsx` — color-coded badge per status: pending (yellow), paid (blue), processing (blue), shipped (purple), delivered (green), cancelled (red), refunded (gray)
- [ ] T018 [P] [US1] Create/extend use-orders hook in `frontend/src/hooks/use-orders.ts` — `useOrders` paginated query with infinite scroll support, optional status filter parameter
- [ ] T019 [US1] Create order history page in `frontend/src/pages/order-history.tsx` — list of order rows with status badge, "Load More" pagination, empty state with "Start Shopping" link; add `/account/orders` as protected route in `frontend/src/App.tsx`

**Checkpoint**: User Story 1 complete — order history list works end-to-end.

---

## Phase 4: User Story 2 — View Order Detail (Priority: P1)

**Goal**: Customers can view full order details including items, status timeline, shipping info, payment summary, tracking number, and reorder action.

**Independent Test**: Navigate to a known order's detail page, verify all fields match the original purchase. Click "Reorder" and verify items are added to cart (with warnings for unavailable items).

### Tests for User Story 2

- [ ] T020 [P] [US2] Integration test for GET /api/v1/orders/{order_number} in `backend/tests/test_orders.py` — test full detail response (items, address, status_history, can_cancel flag), test other user gets 404, test nonexistent order 404
- [ ] T021 [P] [US2] Integration test for POST /api/v1/orders/{order_number}/reorder in `backend/tests/test_orders.py` — test all items added to cart, test partial success (some items out of stock), test with soft-deleted product (unavailable), test other user's order 404
- [ ] T022 [P] [US2] Component test for order detail page in `frontend/tests/order-detail.test.tsx` — test all order fields render, test status timeline, test tracking number display, test "Reorder" button, test "Cancel" button visibility based on can_cancel

### Implementation for User Story 2

- [ ] T023 [US2] Implement order_service.get_order_detail in `backend/app/services/order_service.py` — fetch order by order_number with joined items, status history, payment info; verify ownership; compute can_cancel (status in ['paid', 'processing'] and user is owner); return full detail
- [ ] T024 [US2] Implement order_service.reorder in `backend/app/services/order_service.py` — fetch order items, for each call cart_service.add_item (reuse from Spec 003), collect successes and failures with reasons (out_of_stock, product_deleted, variant_unavailable), return results
- [ ] T025 [US2] Implement GET /api/v1/orders/{order_number} endpoint in `backend/app/api/v1/orders.py` — auth required, call order_service.get_order_detail, return full detail response
- [ ] T026 [US2] Implement POST /api/v1/orders/{order_number}/reorder endpoint in `backend/app/api/v1/orders.py` — auth required, call order_service.reorder, return added_items and unavailable_items
- [ ] T027 [P] [US2] Create order timeline component in `frontend/src/components/order-timeline.tsx` — vertical stepper showing status history with timestamps, highlight current status, show completed/active/upcoming states
- [ ] T028 [P] [US2] Extend use-orders hook in `frontend/src/hooks/use-orders.ts` — add `useOrder(orderNumber)` query for detail, `useReorder(orderNumber)` mutation
- [ ] T029 [US2] Create order detail page in `frontend/src/pages/order-detail.tsx` — display order number, date, status timeline, items with image/name/variant/qty/price/line total, shipping address, shipping method, tracking number (if available), payment summary (subtotal, shipping, tax, total), "Reorder" button, "Cancel" button (if can_cancel); add `/account/orders/:orderNumber` as protected route in `frontend/src/App.tsx`

**Checkpoint**: User Stories 1 & 2 complete — full order viewing experience with reorder.

---

## Phase 5: User Story 3 — Cancel a Pending Order (Priority: P2)

**Goal**: Customers can cancel orders in "paid" or "processing" status with a full refund initiated through Stripe.

**Independent Test**: Place an order, cancel it, verify status changes to "cancelled", refund appears in Stripe test dashboard, stock is restored.

### Tests for User Story 3

- [ ] T030 [P] [US3] Integration test for POST /api/v1/orders/{order_number}/cancel in `backend/tests/test_orders.py` — test cancel from "paid" status (refund + stock restore), test cancel from "processing" status, test cancel from "shipped" status (400 CANNOT_CANCEL), test cancel already cancelled order (400), test cancel other user's order (404), test refund failure handling
- [ ] T031 [P] [US3] Component test for cancel flow in `frontend/tests/order-detail.test.tsx` — test confirmation dialog appears, test cancel button hidden when can_cancel is false, test success updates status badge to "Cancelled"

### Implementation for User Story 3

- [ ] T032 [US3] Implement order_service.cancel_order in `backend/app/services/order_service.py` — validate status is "paid" or "processing", call refund_service.create_refund, if refund succeeds: update order status to "cancelled" + payment_status to "refunded" + set cancelled_at, restore stock (UPDATE product_variants SET stock_quantity = stock_quantity + qty for each OrderItem), log status change with actor_type='customer'; if refund fails: return error without changing order status
- [ ] T033 [US3] Implement POST /api/v1/orders/{order_number}/cancel endpoint in `backend/app/api/v1/orders.py` — auth required, validate ownership, call order_service.cancel_order, return updated order with refund_status
- [ ] T034 [US3] Extend use-orders hook in `frontend/src/hooks/use-orders.ts` — add `useCancelOrder(orderNumber)` mutation, invalidate order query cache on success
- [ ] T035 [US3] Add cancel flow to order detail page in `frontend/src/pages/order-detail.tsx` — "Cancel Order" button (visible only when can_cancel), confirmation dialog ("Are you sure you want to cancel this order?"), optional cancellation reason textarea, on confirm call cancel mutation, on success show updated status

**Checkpoint**: User Story 3 complete — cancellation with refund and stock restoration works end-to-end.

---

## Phase 6: User Story 4 — Manage Wishlist (Priority: P2)

**Goal**: Customers can save products to a wishlist, view wishlisted products, add them to cart, and remove them. Heart icon on product cards/detail toggles wishlist status.

**Independent Test**: Toggle wishlist icon on product page, verify product appears on wishlist page, add to cart from wishlist, remove from wishlist.

### Tests for User Story 4

- [ ] T036 [P] [US4] Integration tests for wishlist endpoints in `backend/tests/test_wishlist.py` — test GET list (paginated, includes product details), test POST add (new item), test POST add duplicate (idempotent 200), test DELETE remove, test DELETE nonexistent (404), test GET check (batch lookup), test unauthenticated (401), test with soft-deleted product (still shows with is_active: false)
- [ ] T037 [P] [US4] Component test for wishlist page in `frontend/tests/wishlist.test.tsx` — test products render with image/name/price/stock, test "Add to Cart" button, test "Remove" button, test out-of-stock label and disabled cart button
- [ ] T038 [P] [US4] Component test for wishlist button on product cards in `frontend/tests/wishlist.test.tsx` — test heart icon toggles filled/unfilled, test optimistic UI update

### Implementation for User Story 4

- [ ] T039 [US4] Implement wishlist_service in `backend/app/services/wishlist_service.py` — `list_wishlist(user_id, cursor, page_size)` with joined product data (name, slug, base_price, primary_image, has_stock, is_active), `add_to_wishlist(user_id, product_id)` idempotent (INSERT ON CONFLICT DO NOTHING), `remove_from_wishlist(user_id, product_id)`, `check_wishlist(user_id, product_ids)` returns wishlisted IDs
- [ ] T040 [US4] Implement wishlist endpoints in `backend/app/api/v1/wishlist.py` — GET /api/v1/users/me/wishlist (paginated), POST /api/v1/users/me/wishlist (add), DELETE /api/v1/users/me/wishlist/{product_id} (remove), GET /api/v1/users/me/wishlist/check (batch lookup, max 50 IDs); all auth required
- [ ] T041 [P] [US4] Create use-wishlist hook in `frontend/src/hooks/use-wishlist.ts` — `useWishlist` paginated query, `useAddToWishlist` mutation, `useRemoveFromWishlist` mutation, `useCheckWishlist(productIds)` query for batch checking on product listings
- [ ] T042 [P] [US4] Create wishlist button component in `frontend/src/components/wishlist-button.tsx` — heart/bookmark icon that toggles filled/unfilled state, optimistic UI update, calls add/remove mutation, accepts productId prop; for unauthenticated users, redirects to login
- [ ] T043 [US4] Create wishlist page in `frontend/src/pages/wishlist.tsx` — grid of product cards with image, name, current price, stock status, "Add to Cart" button (disabled if out of stock), "Remove" button; soft-deleted products shown with "No longer available" label; add `/account/wishlist` as protected route in `frontend/src/App.tsx`
- [ ] T044 [US4] Integrate wishlist button into product card component in `frontend/src/components/product-card.tsx` and product detail page in `frontend/src/pages/product-detail.tsx` — add wishlist toggle icon, use useCheckWishlist for initial state on listing pages

**Checkpoint**: User Story 4 complete — wishlist works end-to-end with toggle on product pages.

---

## Phase 7: User Story 5 — Account Dashboard (Priority: P3)

**Goal**: Customers see a dashboard overview at /account with summary cards linking to orders, addresses, wishlist, and profile. Sidebar/tab navigation for the account area.

**Independent Test**: Log in, navigate to /account, verify all summary cards show accurate data and link to correct sections.

### Tests for User Story 5

- [ ] T045 [P] [US5] Integration test for GET /api/v1/account/dashboard in `backend/tests/test_account.py` — test returns recent_order (or null), address_count, wishlist_count, profile_complete (true when phone filled, false when missing), test unauthenticated (401)
- [ ] T046 [P] [US5] Component test for account dashboard in `frontend/tests/account-dashboard.test.tsx` — test summary cards render with correct data, test cards link to correct sections, test sidebar navigation, test logout action

### Implementation for User Story 5

- [ ] T047 [US5] Implement account dashboard aggregation in `backend/app/services/order_service.py` (or a new `backend/app/services/account_service.py`) — query last order (ORDER BY created_at DESC LIMIT 1), COUNT addresses for user, COUNT wishlist_items for user, check user.phone is not null for profile_complete
- [ ] T048 [US5] Implement GET /api/v1/account/dashboard endpoint in `backend/app/api/v1/account.py` — auth required, return aggregated dashboard data
- [ ] T049 [P] [US5] Create use-account hook in `frontend/src/hooks/use-account.ts` — `useDashboard` query for GET /api/v1/account/dashboard
- [ ] T050 [P] [US5] Create account sidebar component in `frontend/src/components/account-sidebar.tsx` — desktop: vertical sidebar with links to Orders, Addresses, Wishlist, Profile, Log Out; mobile: tab bar or collapsible menu; highlight active section
- [ ] T051 [US5] Create account dashboard page in `frontend/src/pages/account-dashboard.tsx` — summary cards for recent order (with status badge), saved addresses count, wishlist item count, profile completeness; each card links to relevant section; add `/account` as protected route in `frontend/src/App.tsx`
- [ ] T052 [US5] Create account layout wrapper that includes account-sidebar for all /account/* routes in `frontend/src/App.tsx` or a new `frontend/src/components/account-layout.tsx`

**Checkpoint**: All 5 user stories complete — full account area with order management, wishlist, and dashboard.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: E2e tests, edge cases, cross-story integration

- [ ] T053 [P] End-to-end test for cancel-and-refund flow (place order → cancel → verify refund + stock restore) in `backend/tests/test_orders.py` or e2e test framework
- [ ] T054 [P] End-to-end test for reorder flow (place order → reorder → verify cart contents match) in `backend/tests/test_orders.py`
- [ ] T055 [P] Test edge case: cancel order when refund fails — verify order stays in current status and error is returned in `backend/tests/test_orders.py`
- [ ] T056 [P] Test edge case: wishlist product soft-deleted — verify product shows with "No longer available" in `backend/tests/test_wishlist.py`
- [ ] T057 [P] Test edge case: reorder with price-changed items — verify current prices used in `backend/tests/test_orders.py`
- [ ] T058 Verify all monetary values are integer cents across order detail, cancel, and reorder responses
- [ ] T059 Run quickstart.md validation — verify Stripe refund in test mode works, all routes accessible

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — extends existing models
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2)
- **US2 (Phase 4)**: Depends on US1 (Phase 3) — order detail extends from order list
- **US3 (Phase 5)**: Depends on US2 (Phase 4) — cancel button lives on order detail page
- **US4 (Phase 6)**: Depends on Foundational (Phase 2) — INDEPENDENT from US1-US3
- **US5 (Phase 7)**: Depends on US1 and US4 — aggregates data from orders and wishlist
- **Polish (Phase 8)**: Depends on all user stories

### User Story Dependencies

```
Phase 1: Setup
  ↓
Phase 2: Foundational
  ↓ ↘
Phase 3: US1 (Order History)    Phase 6: US4 (Wishlist) ← independent
  ↓                                ↓
Phase 4: US2 (Order Detail)        │
  ↓                                │
Phase 5: US3 (Cancel Order)        │
  ↓                                ↓
Phase 7: US5 (Account Dashboard) ← needs US1 + US4
  ↓
Phase 8: Polish
```

### Within Each User Story

- Tests written first (they will fail until implementation)
- Backend services before API endpoints
- API endpoints before frontend hooks
- Frontend hooks before page components
- Page components integrate everything

### Parallel Opportunities

- **Phase 1**: T002 + T003 (models) in parallel
- **Phase 2**: T006 + T007 + T008 (schemas) in parallel; T009 + T011 + T012 in parallel
- **Phase 3**: T013 + T014 (tests) in parallel; T017 + T018 (frontend) in parallel
- **Phase 4**: T020 + T021 + T022 (tests) in parallel; T027 + T028 (frontend) in parallel
- **Phase 5**: T030 + T031 (tests) in parallel
- **Phase 6**: T036 + T037 + T038 (tests) in parallel; T041 + T042 (frontend) in parallel
- **Phase 7**: T045 + T046 (tests) in parallel; T049 + T050 (frontend) in parallel
- **US1-US3 and US4 can run in parallel** after Foundational completes

---

## Parallel Example: User Story 4 (Wishlist)

```bash
# Launch all tests in parallel:
T036: Integration tests for wishlist endpoints
T037: Component test for wishlist page
T038: Component test for wishlist button

# Launch frontend components in parallel:
T041: use-wishlist hook
T042: wishlist-button component
```

---

## Implementation Strategy

### MVP First (User Stories 1-2)

1. Complete Phase 1: Setup (model extensions + migration)
2. Complete Phase 2: Foundational (schemas, state machine, refund service)
3. Complete Phase 3: US1 — Order History
4. Complete Phase 4: US2 — Order Detail with Reorder
5. **STOP and VALIDATE**: Customers can view and reorder past purchases
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Order history list (MVP view)
3. US2 → Full order details + reorder (MVP complete)
4. US3 → Self-service cancellation (reduced support burden)
5. US4 → Wishlist (engagement feature, independent track)
6. US5 → Account dashboard (ties everything together)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers after Foundational phase:
- **Developer A**: US1 → US2 → US3 (order management track)
- **Developer B**: US4 (wishlist, independent)
- After both: US5 (dashboard aggregates both tracks)
- Then: Polish phase

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Order status state machine is defined in research.md R-002 — enforce at service layer
- Refund uses Stripe Refunds API via refund_service.py — see research.md R-001
- Reorder uses existing cart_service.add_item from Spec 003 — see research.md R-003
- Wishlist is product-level only, not variant-level — see research.md R-004
- Dashboard is a single aggregation endpoint, no denormalized table — see research.md R-005
- Stock restoration on cancellation uses atomic increments — see research.md R-006

# Tasks: Admin Dashboard

**Input**: Design documents from `/specs/005-admin-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/admin-products.md, contracts/admin-categories.md, contracts/admin-orders.md, contracts/admin-users.md, contracts/admin-dashboard.md, quickstart.md

**Tests**: Included per Constitution Principle IV (testing standards mandate integration tests for every API endpoint and component tests for every React page).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Install new dependencies, create admin infrastructure, configure media storage

- [ ] T001 Add `python-multipart` and `cachetools` to `backend/requirements.txt` (or `pyproject.toml`)
- [ ] T002 [P] Add `recharts` and `@uiw/react-md-editor` (or equivalent markdown editor) to `frontend/package.json`
- [ ] T003 [P] Extend backend config with media and dashboard cache settings in `backend/app/core/config.py` — add `MEDIA_ROOT`, `MAX_IMAGE_SIZE_MB`, `MAX_IMAGES_PER_PRODUCT`, `ACCEPTED_IMAGE_TYPES`, `DASHBOARD_CACHE_TTL_SECONDS`
- [ ] T004 [P] Update `.env.example` with new environment variables (media root, image limits, cache TTL)
- [ ] T005 [P] Create `media/products/` directory and add `media/` to `.gitignore`
- [ ] T006 Mount static file serving for media directory in `backend/app/main.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Admin authorization dependency, shared schemas, reusable components that ALL admin stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create `require_admin` FastAPI dependency in `backend/app/core/admin_deps.py` — wraps `get_current_user`, checks `user.role == 'admin'`, raises 403 if not
- [ ] T008 [P] Create admin-specific Pydantic schemas in `backend/app/schemas/admin.py` — AdminProductCreate, AdminProductUpdate, AdminProductListResponse, ImageUploadResponse, AdminCategoryCreate, AdminCategoryUpdate, AdminOrderListResponse, AdminOrderStatusUpdate, AdminRefundRequest, AdminRefundResponse, AdminUserListResponse, AdminUserUpdate, DashboardStatsResponse
- [ ] T009 [P] Create admin route guard component in `frontend/src/components/admin/admin-guard.tsx` — checks if current user has admin role, renders children if admin, shows 403 page if not, redirects to login if unauthenticated
- [ ] T010 [P] Create admin layout component in `frontend/src/components/admin/admin-layout.tsx` — sidebar navigation (Dashboard, Products, Categories, Orders, Users) + content area, responsive design
- [ ] T011 [P] Create reusable data table component in `frontend/src/components/admin/data-table.tsx` — supports search input, filter dropdowns, column sorting, cursor-based pagination with "Load More", configurable columns
- [ ] T012 [P] Add admin-specific types to `frontend/src/lib/types.ts` — AdminProduct, AdminOrder, AdminUser, DashboardStats, KpiData, DailyRevenue, TopProduct
- [ ] T013 [P] Add admin form validation schemas to `frontend/src/lib/validations.ts` — product form, category form, status update, user role update
- [ ] T014 Create `backend/app/api/v1/admin/__init__.py` and register admin sub-router in `backend/app/main.py` with prefix `/api/v1/admin`
- [ ] T015 [P] Add "Admin" link to header navigation in `frontend/src/components/user-menu.tsx` — visible only when user.role === 'admin'
- [ ] T016 Add admin routes in `frontend/src/App.tsx` — `/admin/*` wrapped with admin-guard, using admin-layout

**Checkpoint**: Foundation ready — admin auth, layout, data table, and schemas in place.

---

## Phase 3: User Story 1 — Admin Login and Access Control (Priority: P1) MVP

**Goal**: Admin users can access the admin dashboard. Non-admin users are blocked with a 403 page. Admin API endpoints reject non-admin tokens.

**Independent Test**: Log in as admin → verify dashboard access. Log in as customer → verify 403 on admin routes.

### Tests for User Story 1

- [ ] T017 [P] [US1] Integration test for admin authorization in `backend/tests/test_admin_products.py` (or a shared `test_admin_auth.py`) — test admin user gets 200 on admin endpoints, test customer user gets 403, test unauthenticated gets 401
- [ ] T018 [P] [US1] Component test for admin guard in `frontend/tests/admin/dashboard.test.tsx` — test admin user sees dashboard, test non-admin sees 403 page

### Implementation for User Story 1

- [ ] T019 [US1] Create a minimal admin dashboard page (placeholder) in `frontend/src/pages/admin/dashboard.tsx` — shows "Admin Dashboard" heading, confirms access works; will be enhanced in US5
- [ ] T020 [US1] Verify end-to-end: admin login → header shows "Admin" link → clicking navigates to `/admin` → dashboard loads. Non-admin user → no "Admin" link → direct URL shows 403.

**Checkpoint**: User Story 1 complete — admin access control works end-to-end.

---

## Phase 4: User Story 2 — Manage Products (CRUD) (Priority: P1)

**Goal**: Admins can list, create, edit, and deactivate products. Includes image upload with drag-and-drop reorder and variant management. Slugs auto-generated.

**Independent Test**: Create a product with images and variants, edit its name, deactivate it, verify it disappears from the storefront.

### Tests for User Story 2

- [ ] T021 [P] [US2] Integration tests for admin product endpoints in `backend/tests/test_admin_products.py` — test GET list (search, filter, sort, pagination), test POST create (with slug auto-generation), test PATCH update, test PATCH deactivate, test slug conflict resolution, test customer gets 403
- [ ] T022 [P] [US2] Integration tests for image upload in `backend/tests/test_admin_products.py` — test POST image (valid file), test invalid file type (400), test file too large (400), test max images limit (400), test PATCH image (reorder, alt text), test DELETE image
- [ ] T023 [P] [US2] Integration tests for variant management in `backend/tests/test_admin_products.py` — test POST variant, test PATCH variant, test DELETE variant, test SKU conflict (409)
- [ ] T024 [P] [US2] Component test for product list and form pages in `frontend/tests/admin/products.test.tsx` — test data table renders, test create form validation, test edit form pre-fills data

### Implementation for User Story 2

- [ ] T025 [US2] Implement admin_product_service in `backend/app/services/admin_product_service.py` — `list_products(q, category_id, status, sort, cursor, page_size)` with joined data (category, primary image, total stock, variant count); `create_product(data)` with slug auto-generation; `update_product(id, data)` with slug conflict check; `deactivate_product(id)`
- [ ] T026 [US2] Implement slug auto-generation in `backend/app/services/admin_product_service.py` — `generate_unique_slug(name)`: slugify name, check for conflicts, append `-2`, `-3` etc. if needed
- [ ] T027 [US2] Implement image management in `backend/app/services/admin_product_service.py` — `upload_image(product_id, file, alt_text, position)`: validate type/size/count, save to `MEDIA_ROOT/products/{product_id}/{uuid}.{ext}`, create ProductImage record; `update_image(image_id, alt_text, position)`; `delete_image(image_id)`: remove file + record
- [ ] T028 [US2] Implement variant management in `backend/app/services/admin_product_service.py` — `add_variant(product_id, data)`, `update_variant(variant_id, data)`, `delete_variant(variant_id)` with SKU uniqueness check and order reference check
- [ ] T029 [US2] Implement admin product endpoints in `backend/app/api/v1/admin/products.py` — GET list, POST create, PATCH update, POST image upload (multipart), PATCH/DELETE image, POST/PATCH/DELETE variant; all with `require_admin` dependency
- [ ] T030 [P] [US2] Create use-admin-products hook in `frontend/src/hooks/use-admin-products.ts` — `useAdminProducts` paginated query, `useCreateProduct` mutation, `useUpdateProduct` mutation, `useUploadImage` mutation, `useDeleteImage` mutation, `useAddVariant`, `useUpdateVariant`, `useDeleteVariant` mutations
- [ ] T031 [P] [US2] Create image upload component in `frontend/src/components/admin/image-upload.tsx` — drag-and-drop file upload, image preview grid, drag-and-drop reordering, alt text editing, delete button, max 10 images / 5MB validation
- [ ] T032 [P] [US2] Create variant manager component in `frontend/src/components/admin/variant-manager.tsx` — list of variants with inline editing, add variant form (type, value, SKU, price override, stock), delete variant button
- [ ] T033 [US2] Create product list page in `frontend/src/pages/admin/products.tsx` — data table with columns (thumbnail, name, category, price, stock, status, actions), search/filter/sort, "Create Product" button; add `/admin/products` route
- [ ] T034 [US2] Create product form page in `frontend/src/pages/admin/product-form.tsx` — create/edit form with name, slug (auto-generated, editable), description (markdown editor), category selector, base price, status toggle, image upload section, variant manager section; add `/admin/products/new` and `/admin/products/:id/edit` routes

**Checkpoint**: User Story 2 complete — full product CRUD with images and variants.

---

## Phase 5: User Story 3 — Manage Categories (Priority: P2)

**Goal**: Admins can create, edit, reorder, and delete categories. Tree view with max 2 levels. Deletion protected when products or subcategories are assigned.

**Independent Test**: Create parent + child category, assign a product, attempt to delete child (expect warning), reassign, then delete successfully.

### Tests for User Story 3

- [ ] T035 [P] [US3] Integration tests for admin category endpoints in `backend/tests/test_admin_categories.py` — test GET tree, test POST create (root and child), test PATCH update (name, parent, position), test DELETE empty category, test DELETE with products (400), test DELETE with subcategories (400), test max nesting (400)
- [ ] T036 [P] [US3] Component test for category management page in `frontend/tests/admin/categories.test.tsx` — test tree renders, test create form, test delete confirmation, test drag-and-drop reorder

### Implementation for User Story 3

- [ ] T037 [US3] Implement admin_category_service in `backend/app/services/admin_category_service.py` — `get_category_tree()` returns nested tree with product counts; `create_category(data)` validates nesting depth ≤ 2; `update_category(id, data)` validates nesting on parent change; `delete_category(id)` checks for products and subcategories; `reorder_categories(id, position)`
- [ ] T038 [US3] Implement admin category endpoints in `backend/app/api/v1/admin/categories.py` — GET tree, POST create, PATCH update, DELETE with protection; all with `require_admin`
- [ ] T039 [P] [US3] Create use-admin-categories hook in `frontend/src/hooks/use-admin-categories.ts` — `useAdminCategories` query, `useCreateCategory`, `useUpdateCategory`, `useDeleteCategory` mutations
- [ ] T040 [P] [US3] Create category tree component in `frontend/src/components/admin/category-tree.tsx` — tree view with expand/collapse, product count badges, drag-and-drop reordering, inline actions (edit, delete)
- [ ] T041 [US3] Create category management page in `frontend/src/pages/admin/categories.tsx` — category tree, create category form/dialog, edit dialog, delete confirmation with product/subcategory warnings; add `/admin/categories` route

**Checkpoint**: User Story 3 complete — category tree management works.

---

## Phase 6: User Story 4 — Manage Orders (Priority: P1)

**Goal**: Admins can view all orders across all customers, filter by status/date, update order status with valid transitions, add tracking numbers, and initiate refunds.

**Independent Test**: View all orders, filter by "paid", advance an order to "shipped" with tracking number, initiate a refund on another order.

### Tests for User Story 4

- [ ] T042 [P] [US4] Integration tests for admin order endpoints in `backend/tests/test_admin_orders.py` — test GET list (filter by status, date range, search), test GET detail (includes customer email, admin_notes, valid_transitions), test PATCH status (valid and invalid transitions), test PATCH shipped requires tracking number, test POST refund (success), test POST refund already refunded (400), test status history logging with admin actor
- [ ] T043 [P] [US4] Component test for admin order pages in `frontend/tests/admin/orders.test.tsx` — test order data table renders with all columns, test status dropdown shows only valid transitions, test tracking number input on ship transition, test refund confirmation dialog

### Implementation for User Story 4

- [ ] T044 [US4] Implement admin_order_service in `backend/app/services/admin_order_service.py` — `list_orders(status, date_from, date_to, q, cursor, page_size)` lists all orders (no user filter) with customer info; `get_order_detail(order_id)` returns full detail + customer email + admin_notes + valid_transitions + can_refund; `update_status(order_id, new_status, tracking_number, note, admin_id)` validates transition, requires tracking for "shipped", logs to OrderStatusHistory with actor_type='admin'; `refund_order(order_id, reason, admin_id)` uses refund_service, updates payment_status to 'refunded', logs status change
- [ ] T045 [US4] Implement admin order endpoints in `backend/app/api/v1/admin/orders.py` — GET list, GET detail, PATCH status, POST refund, PATCH notes; all with `require_admin`
- [ ] T046 [P] [US4] Create use-admin-orders hook in `frontend/src/hooks/use-admin-orders.ts` — `useAdminOrders` paginated query (with status/date filters), `useAdminOrder` detail query, `useUpdateOrderStatus` mutation, `useRefundOrder` mutation, `useUpdateOrderNotes` mutation
- [ ] T047 [US4] Create admin order list page in `frontend/src/pages/admin/orders.tsx` — data table with columns (order number, customer name, date, total, status badge, actions), multi-select status filter, date range picker, search by order number/customer; add `/admin/orders` route
- [ ] T048 [US4] Create admin order detail page in `frontend/src/pages/admin/order-detail.tsx` — all order info + customer email + admin notes field, status dropdown (only valid_transitions), tracking number input (shown when transitioning to shipped), refund button (when can_refund), status history timeline; add `/admin/orders/:id` route

**Checkpoint**: User Story 4 complete — order management with status updates and refunds.

---

## Phase 7: User Story 5 — View Analytics Dashboard (Priority: P2)

**Goal**: Admin dashboard home shows KPI cards, daily revenue chart, top products, and recent orders. Configurable time range (7/30/90 days). Data cached for 5 minutes.

**Independent Test**: Seed orders across different dates, verify KPI values and chart data match expected calculations.

### Tests for User Story 5

- [ ] T049 [P] [US5] Integration test for GET /api/v1/admin/dashboard/stats in `backend/tests/test_admin_dashboard.py` — test returns correct revenue/orders/avg/customers for 30-day period, test 7-day and 90-day periods, test caching (second call within 5 min returns same computed_at), test with no orders (zeros), test customer gets 403
- [ ] T050 [P] [US5] Component test for admin dashboard page in `frontend/tests/admin/dashboard.test.tsx` — test KPI cards render with correct values, test revenue chart renders, test top products list, test recent orders list, test time range selector

### Implementation for User Story 5

- [ ] T051 [US5] Implement dashboard_service in `backend/app/services/dashboard_service.py` — `get_stats(days)`: compute total_revenue (SUM of paid order totals), total_orders (COUNT), average_order_value, total_customers, daily_revenue (GROUP BY date), top_products (JOIN order_items, GROUP BY product, ORDER BY count DESC LIMIT 5), recent_orders (ORDER BY created_at DESC LIMIT 5). Use cachetools.TTLCache with 5-minute TTL, keyed by days.
- [ ] T052 [US5] Implement GET /api/v1/admin/dashboard/stats endpoint in `backend/app/api/v1/admin/dashboard.py` — query param `days` (7/30/90, default 30), call dashboard_service.get_stats, return DashboardStatsResponse
- [ ] T053 [P] [US5] Create use-admin-dashboard hook in `frontend/src/hooks/use-admin-dashboard.ts` — `useDashboardStats(days)` query with refetch on time range change
- [ ] T054 [P] [US5] Create KPI card component in `frontend/src/components/admin/kpi-card.tsx` — displays label, value (formatted), optional trend indicator, clickable for navigation
- [ ] T055 [P] [US5] Create revenue chart component in `frontend/src/components/admin/revenue-chart.tsx` — line or bar chart using recharts, daily revenue data, formatted currency Y-axis, date X-axis
- [ ] T056 [US5] Enhance admin dashboard page in `frontend/src/pages/admin/dashboard.tsx` — time range selector (7/30/90 days), KPI cards row (revenue, orders, AOV, customers), revenue chart, top products list (product name, order count, revenue), recent orders mini-table (order number, customer, total, status badge)

**Checkpoint**: User Story 5 complete — analytics dashboard with live KPIs and charts.

---

## Phase 8: User Story 6 — Manage Users (Priority: P3)

**Goal**: Admins can view all users, change roles (customer ↔ admin), activate/deactivate accounts. Last-admin protection prevents lockout.

**Independent Test**: View users, promote a customer to admin (verify access), deactivate a user (verify login blocked), reactivate.

### Tests for User Story 6

- [ ] T057 [P] [US6] Integration tests for admin user endpoints in `backend/tests/test_admin_users.py` — test GET list (search, filter by role/status, pagination), test PATCH promote to admin, test PATCH demote to customer, test PATCH deactivate, test PATCH reactivate, test last-admin protection (400), test cannot edit name/email
- [ ] T058 [P] [US6] Component test for user management page in `frontend/tests/admin/users.test.tsx` — test user data table renders, test role change dropdown, test activate/deactivate toggle, test last-admin error display

### Implementation for User Story 6

- [ ] T059 [US6] Implement admin_user_service in `backend/app/services/admin_user_service.py` — `list_users(q, role, is_active, cursor, page_size)` with order_count subquery; `update_user(user_id, role, is_active)` with last-admin check (count active admins, reject if would drop to 0)
- [ ] T060 [US6] Implement admin user endpoints in `backend/app/api/v1/admin/users.py` — GET list, PATCH update (role, is_active only); with `require_admin`
- [ ] T061 [P] [US6] Create use-admin-users hook in `frontend/src/hooks/use-admin-users.ts` — `useAdminUsers` paginated query (with search, role/status filters), `useUpdateUser` mutation
- [ ] T062 [US6] Create user management page in `frontend/src/pages/admin/users.tsx` — data table with columns (email, name, role badge, registration date, order count, active status toggle), search, filter by role/status, role change dropdown per row, activate/deactivate toggle per row, last-admin error handling; add `/admin/users` route

**Checkpoint**: All 6 user stories complete — full admin dashboard.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: E2e tests, edge cases, security, responsive design

- [ ] T063 [P] End-to-end test: create product with images + variants → verify on storefront → deactivate → verify hidden from storefront
- [ ] T064 [P] End-to-end test: order lifecycle (paid → processing → shipped with tracking → delivered) via admin panel
- [ ] T065 [P] Test edge case: deactivated product in customer cart → checkout shows unavailable
- [ ] T066 [P] Test edge case: delete category with products → verify blocked with correct error
- [ ] T067 [P] Test edge case: concurrent admin status updates → second update fails gracefully
- [ ] T068 [P] Test edge case: refund already-refunded order → verify blocked
- [ ] T069 Verify admin sidebar navigation is responsive (collapses on mobile)
- [ ] T070 Run quickstart.md validation — verify media directory setup, image upload, dashboard stats, admin seeding
- [ ] T071 Verify all admin API endpoints return 403 for non-admin users (comprehensive auth sweep)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — minimal placeholder dashboard
- **US2 (Phase 4)**: Depends on US1 — product CRUD
- **US3 (Phase 5)**: Depends on Foundational — INDEPENDENT from US2, US4
- **US4 (Phase 6)**: Depends on US1 — order management
- **US5 (Phase 7)**: Depends on US1 — analytics dashboard enhancement
- **US6 (Phase 8)**: Depends on Foundational — INDEPENDENT from US2-US5
- **Polish (Phase 9)**: Depends on all user stories

### User Story Dependencies

```
Phase 1: Setup
  ↓
Phase 2: Foundational
  ↓
Phase 3: US1 (Access Control)
  ↓ ↘ ↘ ↘
  │  Phase 5: US3 (Categories) ← independent
  │  Phase 8: US6 (Users) ← independent
  ↓
Phase 4: US2 (Products)    Phase 6: US4 (Orders)    Phase 7: US5 (Analytics)
  ↓                           ↓                        ↓
Phase 9: Polish (after all complete)
```

### Within Each User Story

- Tests written first (they will fail until implementation)
- Backend services before API endpoints
- API endpoints before frontend hooks
- Frontend hooks before page components
- Page components integrate everything

### Parallel Opportunities

- **Phase 2**: T008-T013 (schemas, components, types) all in parallel
- **Phase 4**: T021-T024 (tests) in parallel; T030-T032 (frontend) in parallel
- **Phase 5**: T035+T036 (tests) in parallel; T039+T040 in parallel
- **Phase 6**: T042+T043 (tests) in parallel; T046 in parallel with backend
- **Phase 7**: T049+T050 (tests) in parallel; T053-T055 (frontend) in parallel
- **Phase 8**: T057+T058 (tests) in parallel
- **US2, US3, US4, US5, US6 can all run in parallel** after US1 (Phase 3) completes — they work on different endpoint domains

---

## Parallel Example: User Story 2 (Products)

```bash
# Launch all tests in parallel:
T021: Integration tests for product CRUD
T022: Integration tests for image upload
T023: Integration tests for variant management
T024: Component test for product pages

# Launch frontend components in parallel:
T030: use-admin-products hook
T031: image-upload component
T032: variant-manager component
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (admin auth, layout, data table)
3. Complete Phase 3: US1 — Admin access control (minimal dashboard)
4. Complete Phase 6: US4 — Order management (daily operational need)
5. **STOP and VALIDATE**: Admin can log in and process orders
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Admin infrastructure ready
2. US1 → Access control (gate for everything)
3. US4 → Order management (daily ops — highest business value after access)
4. US2 → Product management (catalog maintenance)
5. US3 → Category management (organizational)
6. US5 → Analytics dashboard (business insight)
7. US6 → User management (infrequent admin task)
8. Polish → E2e tests, edge cases

### Parallel Team Strategy

With multiple developers after US1:
- **Developer A**: US2 (products — largest surface area)
- **Developer B**: US4 (orders — daily ops priority)
- **Developer C**: US5 (analytics) + US6 (users) — smaller stories
- After: Developer A takes US3 (categories), all contribute to Polish

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- No new database tables — all admin endpoints operate on existing models from Specs 001-004
- Admin auth uses `require_admin` dependency at router level — see research.md R-001
- Image storage is local filesystem — see research.md R-002
- Dashboard uses in-memory TTL cache (cachetools) — see research.md R-004
- Slug auto-generation uses slugify + conflict resolution — see research.md R-005
- Admin refund reuses refund_service from Spec 004 — see research.md R-006
- Last-admin protection prevents lockout — see research.md R-007

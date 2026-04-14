# Tasks: Product Catalog

**Input**: Design documents from `/specs/001-product-catalog/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Docker, and basic directory structure

- [x] T001 Create backend project directory structure: `backend/app/api/v1/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/core/`, `backend/tests/`
- [x] T002 Create frontend project directory structure: `frontend/src/components/`, `frontend/src/components/ui/`, `frontend/src/pages/`, `frontend/src/hooks/`, `frontend/src/lib/`
- [x] T003 [P] Initialize Python backend with FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, uvicorn, httpx in `backend/pyproject.toml` and `backend/requirements.txt`
- [x] T004 [P] Initialize React frontend with Vite, TypeScript strict mode, Tailwind CSS, TanStack Query, zod in `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/tailwind.config.ts`
- [x] T005 [P] Initialize shadcn/ui in `frontend/` and install core components (Button, Card, Input, Select, Slider, Badge, Skeleton, Dialog, Form)
- [x] T006 Create `docker-compose.yml` with PostgreSQL 16, backend (FastAPI with hot reload), and frontend (Vite with HMR) services
- [x] T007 Create `.env.example` with all required environment variables (DATABASE_URL, SECRET_KEY, CORS_ORIGINS, etc.)
- [x] T008 Create `backend/Dockerfile` and `frontend/Dockerfile` for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure, shared database models, and frontend API layer that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create FastAPI application entry point with CORS middleware, API router mount at `/api/v1/`, and OpenAPI config in `backend/app/main.py`
- [x] T010 Create async SQLAlchemy engine, session factory, and Base declarative model in `backend/app/core/database.py`
- [x] T011 Create dependency injection for async DB session and current user (optional auth) in `backend/app/core/deps.py`
- [x] T012 Create application settings from environment variables in `backend/app/core/config.py`
- [x] T013 Initialize Alembic with async SQLAlchemy configuration in `backend/alembic.ini` and `backend/alembic/env.py`
- [x] T014 [P] Create Category SQLAlchemy model (id UUID PK, name, slug unique, parent_id self-FK nullable, position, created_at, updated_at) with indexes in `backend/app/models/category.py`
- [x] T015 [P] Create Product SQLAlchemy model (id UUID PK, name, slug unique, description, base_price int, category_id FK, is_active, search_vector tsvector, deleted_at, created_at, updated_at) with indexes and GIN index on search_vector in `backend/app/models/product.py`
- [x] T016 [P] Create ProductImage SQLAlchemy model (id UUID PK, product_id FK cascade, url, alt_text, position, created_at, updated_at) with indexes in `backend/app/models/product.py`
- [x] T017 [P] Create ProductVariant SQLAlchemy model (id UUID PK, product_id FK cascade, variant_type, variant_value, sku unique, price_override nullable int, stock_quantity, created_at, updated_at) with unique constraint on (product_id, variant_type, variant_value) in `backend/app/models/product.py`
- [x] T018 Generate Alembic migration for Category, Product, ProductImage, and ProductVariant tables including search_vector trigger in `backend/alembic/versions/`
- [x] T019 Create cursor-based pagination utility (encode/decode opaque base64 cursors, apply WHERE/ORDER/LIMIT, return has_next_page) in `backend/app/core/pagination.py`
- [x] T020 Create consistent error response format (`{"detail": "message", "code": "ERROR_CODE"}`) and exception handlers in `backend/app/core/errors.py`
- [x] T021 Create Pydantic base schemas (PaginatedResponse, CursorParams, ErrorResponse) in `backend/app/schemas/common.py`
- [x] T022 Create API client with base URL, error handling, and TypeScript types in `frontend/src/lib/api-client.ts`
- [x] T023 Create shared TypeScript types (Product, Category, ProductImage, ProductVariant, PaginatedResponse) in `frontend/src/lib/types.ts`
- [x] T024 Create price formatting utility (cents to display string) and other shared helpers in `frontend/src/lib/utils.ts`
- [x] T025 Create TanStack Query provider setup in `frontend/src/App.tsx` with React Router (routes for `/products` and `/products/:slug`)
- [x] T026 Create seed data script with sample categories (2 levels), products, images, and variants in `backend/app/scripts/seed.py`

**Checkpoint**: Foundation ready — database running, models migrated, seed data available, frontend scaffolded. User story implementation can now begin.

---

## Phase 3: User Story 1 — Browse Products by Category (Priority: P1) MVP

**Goal**: Shoppers can browse products organized by hierarchical categories with product counts, URL-driven navigation, and empty states.

**Independent Test**: Navigate to a category page, verify only matching products appear with correct counts, subcategories work, URL reflects selection.

### Implementation for User Story 1

- [ ] T027 [P] [US1] Create Category Pydantic schemas (CategoryTree with nested children and product_count) in `backend/app/schemas/category.py`
- [ ] T028 [P] [US1] Create Product list Pydantic schemas (ProductListItem with id, name, slug, base_price, primary_image, average_rating, review_count, has_stock; ProductListResponse with cursor pagination) in `backend/app/schemas/product.py`
- [ ] T029 [US1] Implement CategoryService with get_category_tree() using recursive CTE, computing product_count for active non-deleted products in `backend/app/services/category_service.py`
- [ ] T030 [US1] Implement ProductService.list_products() with category_id filter, cursor-based pagination (default page_size=20), and default sort by newest in `backend/app/services/product_service.py`
- [ ] T031 [P] [US1] Create GET `/api/v1/categories` endpoint returning nested category tree in `backend/app/api/v1/categories.py`
- [ ] T032 [P] [US1] Create GET `/api/v1/products` endpoint with category_id query param and cursor pagination in `backend/app/api/v1/products.py`
- [ ] T033 [US1] Register categories and products routers on the API v1 router in `backend/app/api/v1/__init__.py`
- [ ] T034 [P] [US1] Create CategoryNav component displaying hierarchical category list with product counts and active state highlighting in `frontend/src/components/category-nav.tsx`
- [ ] T035 [P] [US1] Create ProductCard component showing product thumbnail, name, price, rating, and stock badge in `frontend/src/components/product-card.tsx`
- [ ] T036 [US1] Create useCategories TanStack Query hook (GET /api/v1/categories with staleTime for caching) in `frontend/src/hooks/use-categories.ts`
- [ ] T037 [US1] Create useProducts TanStack Query hook (GET /api/v1/products with category_id, pagination via useInfiniteQuery) in `frontend/src/hooks/use-products.ts`
- [ ] T038 [US1] Create ProductListPage with CategoryNav sidebar, product grid, empty state, and URL sync (category query param) in `frontend/src/pages/product-list.tsx`

**Checkpoint**: Shoppers can browse products by category. Category navigation works, products display in a grid, URLs are bookmarkable. This is the MVP.

---

## Phase 4: User Story 2 — View Product Detail Page (Priority: P1)

**Goal**: Shoppers can view a full product detail page with image gallery, variant selection, pricing, and an "Add to Cart" button.

**Independent Test**: Navigate to `/products/:slug`, verify all fields render, select a variant and confirm price/stock updates, verify SEO meta tags.

### Implementation for User Story 2

- [ ] T039 [US2] Create Product detail Pydantic schema (ProductDetail with all fields: images ordered by position, variants with resolved price, category with parent breadcrumb, rating_distribution) in `backend/app/schemas/product.py`
- [ ] T040 [US2] Implement ProductService.get_by_slug() returning full product detail with images, variants, category breadcrumb, average_rating, review_count, and rating_distribution in `backend/app/services/product_service.py`
- [ ] T041 [US2] Create GET `/api/v1/products/{slug}` endpoint returning ProductDetail (404 if not found or soft-deleted) in `backend/app/api/v1/products.py`
- [ ] T042 [P] [US2] Create ProductGallery component with main image display and thumbnail navigation strip in `frontend/src/components/product-gallery.tsx`
- [ ] T043 [P] [US2] Create VariantSelector component with grouped options (size, color), active selection state, price/stock update on selection, and out-of-stock disabled state in `frontend/src/components/variant-selector.tsx`
- [ ] T044 [P] [US2] Create RatingDisplay component showing star rating, average score, and review count in `frontend/src/components/rating-display.tsx`
- [ ] T045 [US2] Create useProduct TanStack Query hook (GET /api/v1/products/:slug) in `frontend/src/hooks/use-products.ts`
- [ ] T046 [US2] Create ProductDetailPage with gallery, variant selector, price display, "Add to Cart" button, category breadcrumb, rating summary, and SEO meta tags (title, description, Open Graph) in `frontend/src/pages/product-detail.tsx`
- [ ] T047 [US2] Handle product-not-found (404) state with friendly message and link back to catalog in `frontend/src/pages/product-detail.tsx`

**Checkpoint**: Shoppers can view full product details, browse images, select variants, and see updated pricing. Product pages have SEO meta tags.

---

## Phase 5: User Story 3 — Search Products (Priority: P2)

**Goal**: Shoppers can search for products by name or description with relevance-ranked results, friendly empty states, and URL-persisted queries.

**Independent Test**: Search for a known product name, verify it appears in results. Search for a partial name, verify relevant results. Search nonsense, verify empty state.

### Implementation for User Story 3

- [ ] T048 [US3] Add full-text search to ProductService.list_products() — accept `q` parameter, query against search_vector using plainto_tsquery, rank results with ts_rank in `backend/app/services/product_service.py`
- [ ] T049 [US3] Add `q` query parameter to GET `/api/v1/products` endpoint, passing through to ProductService in `backend/app/api/v1/products.py`
- [ ] T050 [US3] Create SearchBar component with input field, submit handler, and search icon — accessible from all pages via layout header in `frontend/src/components/search-bar.tsx`
- [ ] T051 [US3] Add SearchBar to application layout/header so it appears on every page in `frontend/src/App.tsx`
- [ ] T052 [US3] Update useProducts hook to accept `q` parameter and pass to API in `frontend/src/hooks/use-products.ts`
- [ ] T053 [US3] Update ProductListPage to handle search query from URL params, display search results with query shown, and show friendly empty state with suggestions when no results match in `frontend/src/pages/product-list.tsx`

**Checkpoint**: Full-text search works across product names and descriptions. Results are relevance-ranked. Empty states guide users.

---

## Phase 6: User Story 4 — Filter and Sort Product Listings (Priority: P2)

**Goal**: Shoppers can filter products by price range, rating, and stock availability, sort by price/newest/popular, with URL-synced state, removable filter chips, and no full page reloads.

**Independent Test**: Apply a price filter, verify correct products. Apply sort, verify order. Combine filters. Clear all, verify full list.

### Implementation for User Story 4

- [ ] T054 [US4] Add filter parameters (min_price, max_price, min_rating, in_stock) and sort parameter (price_asc, price_desc, newest, popular) to ProductService.list_products() with appropriate WHERE clauses and ORDER BY in `backend/app/services/product_service.py`
- [ ] T055 [US4] Add filter and sort query parameters to GET `/api/v1/products` endpoint with validation via Pydantic in `backend/app/api/v1/products.py`
- [ ] T056 [P] [US4] Create FilterSidebar component with price range slider (min/max), rating selector (1-5 stars), and in-stock toggle in `frontend/src/components/filter-sidebar.tsx`
- [ ] T057 [P] [US4] Create SortSelect component with dropdown for price_asc, price_desc, newest, popular in `frontend/src/components/sort-select.tsx`
- [ ] T058 [US4] Update useProducts hook to accept all filter and sort parameters in `frontend/src/hooks/use-products.ts`
- [ ] T059 [US4] Update ProductListPage to integrate FilterSidebar and SortSelect, sync all filter/sort state to URL query params, display active filters as removable Badge chips, include "Clear all filters" action, and update results without page reload in `frontend/src/pages/product-list.tsx`

**Checkpoint**: Full filtering and sorting functional. URL state enables bookmarking/sharing of filtered views. No page reloads on filter change.

---

## Phase 7: User Story 5 — View Product Reviews (Priority: P3)

**Goal**: Shoppers can read paginated product reviews with star ratings, reviewer names, dates, and see an aggregate rating distribution.

**Independent Test**: Load a product with reviews, verify reviews render with correct data, pagination works, and rating summary is accurate.

### Implementation for User Story 5

- [ ] T060 [P] [US5] Create Review SQLAlchemy model (id UUID PK, product_id FK, user_id FK, rating smallint CHECK 1-5, text, created_at, updated_at) with unique constraint on (user_id, product_id) and indexes in `backend/app/models/review.py`
- [ ] T061 [US5] Generate Alembic migration for Review table in `backend/alembic/versions/`
- [ ] T062 [US5] Create Review Pydantic schemas (ReviewItem with reviewer_name, ReviewListResponse with cursor pagination) in `backend/app/schemas/review.py`
- [ ] T063 [US5] Implement ReviewService.list_reviews() with product slug lookup, cursor-based pagination (default page_size=10), ordered by created_at desc in `backend/app/services/review_service.py`
- [ ] T064 [US5] Create GET `/api/v1/products/{slug}/reviews` endpoint with cursor pagination in `backend/app/api/v1/reviews.py`
- [ ] T065 [US5] Register reviews router on the API v1 router in `backend/app/api/v1/__init__.py`
- [ ] T066 [P] [US5] Create ReviewList component displaying individual reviews (reviewer name, star rating, text, date) with "Load more" pagination in `frontend/src/components/review-list.tsx`
- [ ] T067 [P] [US5] Create RatingDistribution component showing bar chart of 1-5 star counts alongside average rating in `frontend/src/components/rating-display.tsx`
- [ ] T068 [US5] Create useReviews TanStack Query hook (GET /api/v1/products/:slug/reviews with useInfiniteQuery) in `frontend/src/hooks/use-reviews.ts`
- [ ] T069 [US5] Integrate ReviewList and RatingDistribution into ProductDetailPage below the product details section in `frontend/src/pages/product-detail.tsx`
- [ ] T070 [US5] Add review seed data (sample reviews for products) to seed script in `backend/app/scripts/seed.py`

**Checkpoint**: Product pages display reviews with ratings, text, pagination, and an aggregate rating distribution chart.

---

## Phase 8: User Story 6 — Submit a Product Review (Priority: P3)

**Goal**: Authenticated customers who purchased a product can submit or edit their review.

**Independent Test**: Log in as a user who purchased a product, submit a review, verify it appears. Try as a non-purchaser, verify form is hidden.

### Implementation for User Story 6

- [ ] T071 [US6] Create Review submission Pydantic schemas (ReviewCreate with rating 1-5, text 1-5000 chars; ReviewUpdate) in `backend/app/schemas/review.py`
- [ ] T072 [US6] Implement ReviewService.create_review() with purchase verification (check orders table, fallback to auth-only if unavailable), duplicate check, and save in `backend/app/services/review_service.py`
- [ ] T073 [US6] Implement ReviewService.update_review() with ownership check in `backend/app/services/review_service.py`
- [ ] T074 [US6] Create POST `/api/v1/products/{slug}/reviews` endpoint (auth required) returning 201 with created review in `backend/app/api/v1/reviews.py`
- [ ] T075 [US6] Create PUT `/api/v1/products/{slug}/reviews/{review_id}` endpoint (auth required, owner only) in `backend/app/api/v1/reviews.py`
- [ ] T076 [US6] Create ReviewForm component with star rating input (1-5), text area, zod validation, submit handler, and error display in `frontend/src/components/review-form.tsx`
- [ ] T077 [US6] Create useSubmitReview and useUpdateReview TanStack Query mutation hooks in `frontend/src/hooks/use-reviews.ts`
- [ ] T078 [US6] Integrate ReviewForm into ProductDetailPage — show form for eligible users, show "purchase required" message for ineligible users, show existing review with edit option for users who already reviewed in `frontend/src/pages/product-detail.tsx`

**Checkpoint**: Authenticated purchasers can submit and edit reviews. Non-purchasers see appropriate messaging.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T079 [P] Add loading skeleton states to ProductListPage (product card skeletons during fetch) in `frontend/src/pages/product-list.tsx`
- [ ] T080 [P] Add loading skeleton states to ProductDetailPage (gallery, details, reviews skeletons) in `frontend/src/pages/product-detail.tsx`
- [ ] T081 [P] Add error boundary component for graceful error handling across all pages in `frontend/src/components/error-boundary.tsx`
- [ ] T082 [P] Add responsive design breakpoints to ProductListPage (1-col mobile, 2-col tablet, 3-4 col desktop grid) and FilterSidebar (drawer on mobile) in relevant component files
- [ ] T083 Verify all API endpoints return consistent error format (`{"detail", "code"}`) and appropriate HTTP status codes across all routes in `backend/app/api/v1/`
- [ ] T084 Verify soft delete filtering is applied to all product queries (list, detail, search, category counts) in `backend/app/services/product_service.py`
- [ ] T085 Add placeholder image handling when product has no images in `frontend/src/components/product-card.tsx` and `frontend/src/components/product-gallery.tsx`
- [ ] T086 Validate quickstart.md end-to-end: `docker compose up`, run migrations, seed data, verify all 6 API endpoints respond correctly, verify frontend pages render

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 Browse by Category (Phase 3)**: Depends on Foundational — no other story dependencies
- **US2 Product Detail (Phase 4)**: Depends on Foundational — independent of US1 (though benefits from it for navigation)
- **US3 Search (Phase 5)**: Depends on Foundational + ProductService from US1 (T030)
- **US4 Filter & Sort (Phase 6)**: Depends on Foundational + ProductService from US1 (T030)
- **US5 View Reviews (Phase 7)**: Depends on Foundational — independent (adds Review model)
- **US6 Submit Review (Phase 8)**: Depends on US5 (Review model and service must exist)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational
    ↓
    ├── US1 (P1): Browse by Category ─────┐
    ├── US2 (P1): Product Detail ─────────┤
    │       ↓                              │
    ├── US3 (P2): Search (extends US1)     │
    ├── US4 (P2): Filter & Sort (extends US1)
    │                                      │
    ├── US5 (P3): View Reviews ────────────┤
    │       ↓                              │
    └── US6 (P3): Submit Review            │
                                           ↓
                                    Phase 9: Polish
```

### Within Each User Story

- Pydantic schemas before service implementation
- Service implementation before API endpoints
- Backend endpoints before frontend hooks
- Frontend hooks before page integration

### Parallel Opportunities

- T003, T004, T005 (Setup: backend init, frontend init, shadcn setup)
- T014, T015, T016, T017 (Foundational: all database models)
- T027, T028 (US1: category and product schemas)
- T031, T032 (US1: category and product endpoints)
- T034, T035 (US1: CategoryNav and ProductCard components)
- T042, T043, T044 (US2: Gallery, VariantSelector, RatingDisplay components)
- T056, T057 (US4: FilterSidebar and SortSelect components)
- T060, T066, T067 (US5: Review model and frontend components)
- T079, T080, T081, T082 (Polish: all skeleton/error/responsive tasks)

---

## Parallel Example: User Story 1

```bash
# Launch schemas in parallel:
Task: "Create Category Pydantic schemas in backend/app/schemas/category.py"
Task: "Create Product list Pydantic schemas in backend/app/schemas/product.py"

# After services complete, launch endpoints in parallel:
Task: "Create GET /api/v1/categories endpoint in backend/app/api/v1/categories.py"
Task: "Create GET /api/v1/products endpoint in backend/app/api/v1/products.py"

# Launch frontend components in parallel:
Task: "Create CategoryNav component in frontend/src/components/category-nav.tsx"
Task: "Create ProductCard component in frontend/src/components/product-card.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 — Browse by Category
4. **STOP and VALIDATE**: Navigate categories, verify product grid, check pagination
5. Deploy/demo if ready — shoppers can browse products by category

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 Browse by Category → **MVP!** Shoppers can discover products
3. Add US2 Product Detail → Shoppers can view full product info and select variants
4. Add US3 Search → Shoppers can find specific products quickly
5. Add US4 Filter & Sort → Shoppers can narrow results to their needs
6. Add US5 View Reviews → Shoppers can read reviews for trust/confidence
7. Add US6 Submit Review → Customers can contribute reviews
8. Polish → Skeletons, error handling, responsive design

### Parallel Team Strategy

With multiple developers after Foundational is complete:

- **Developer A**: US1 (Browse) → US3 (Search) → US4 (Filter/Sort) — listing-focused
- **Developer B**: US2 (Product Detail) → US5 (View Reviews) → US6 (Submit Review) — detail-page-focused

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Foundational phase
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All monetary values use cents (integers) in DB and API; format on frontend only
- All list endpoints use cursor-based pagination per constitution

# Research: Product Catalog

**Feature**: Product Catalog
**Date**: 2026-04-14
**Status**: Complete

## R-001: PostgreSQL Full-Text Search Strategy

**Decision**: Use PostgreSQL native full-text search with `tsvector` and `tsquery` via SQLAlchemy.

**Rationale**: PostgreSQL's built-in FTS is sufficient for a catalog of 1,000–10,000+ products. It requires no additional infrastructure, supports ranking by relevance (`ts_rank`), partial matching with prefix search (`:*` operator), and integrates natively with SQLAlchemy. It eliminates the need for a separate search service (Elasticsearch, Meilisearch) at this scale.

**Alternatives considered**:
- **Elasticsearch/OpenSearch**: Overkill for this scale; adds operational complexity (separate cluster, index sync). Consider if product count exceeds 100k or advanced features like fuzzy matching and faceted search are needed.
- **Meilisearch**: Simpler than Elasticsearch but still an extra service. Good option if FTS proves insufficient.
- **pg_trgm (trigram matching)**: Good for typo tolerance but slower for relevance ranking at scale. Can be added later as a complement.

**Implementation notes**:
- Create a `search_vector` column (type `tsvector`) on the products table.
- Maintain it via a database trigger on INSERT/UPDATE that combines `name` (weight A) and `description` (weight B).
- Create a GIN index on the `search_vector` column.
- Query with `tsquery` using `plainto_tsquery` for user input and `ts_rank` for ordering.

## R-002: Cursor-Based Pagination Pattern

**Decision**: Use opaque cursor tokens encoding the sort key + primary key, with `after` parameter for forward pagination.

**Rationale**: Constitution Principle VI mandates cursor-based pagination. Using the sort key + UUID as cursor ensures stable pagination even with concurrent inserts/deletes and performs well (no OFFSET scanning).

**Alternatives considered**:
- **Offset-based pagination**: Simpler but breaks with concurrent modifications and degrades at high offsets. Rejected per constitution.
- **Keyset pagination with exposed values**: Works but leaks internal data. Opaque base64-encoded cursors are preferred.

**Implementation notes**:
- Cursor format: base64-encoded JSON of `{"sort_value": ..., "id": "uuid"}`.
- Query pattern: `WHERE (sort_col, id) > (:sort_value, :cursor_id) ORDER BY sort_col, id LIMIT :page_size + 1`.
- Return `has_next_page` by requesting `page_size + 1` and trimming.
- Default page size: 20 for product listings, 10 for reviews.

## R-003: Product Variant Modeling

**Decision**: Use a separate `product_variants` table with per-variant price override and stock quantity. Variant types (size, color, etc.) are modeled as a `variant_type`/`variant_value` pair on each variant row.

**Rationale**: This is the simplest approach that supports the spec's requirements. Each variant has its own price and stock, which maps directly to a row-per-variant model. More complex EAV (entity-attribute-value) or option-group models are unnecessary given the spec's scope.

**Alternatives considered**:
- **JSONB attributes on product**: Flexible but hard to query, filter, and validate. No FK constraints possible.
- **Separate option groups + option values + SKU matrix**: More normalized but adds 3+ tables for a feature that the spec describes as simple variant selection. Overkill for v1.
- **Single table with variant columns**: Doesn't scale if variant types vary between products.

**Implementation notes**:
- `product_variants` table: `id`, `product_id` (FK), `variant_type` (e.g., "Size"), `variant_value` (e.g., "Large"), `price_override` (nullable, in cents — falls back to product base price if null), `stock_quantity`, `sku`, `created_at`, `updated_at`.
- A product with no variants is still purchasable at its base price — the frontend hides the variant selector.

## R-004: Image Storage Strategy

**Decision**: Store image URLs in the database. Images themselves are served from an external source (CDN, cloud storage, or local file server in development).

**Rationale**: The spec states "Product images are stored as URLs (either external CDN or local file storage in v1)." Image upload/management is handled by the admin dashboard (spec 005), not this feature.

**Implementation notes**:
- `product_images` table: `id`, `product_id` (FK), `url`, `alt_text`, `position` (integer for ordering), `created_at`, `updated_at`.
- Frontend fetches image URLs from the API and renders them directly.
- Placeholder image URL used when a product has no images.

## R-005: Review Purchase Verification

**Decision**: Enforce purchase verification for review submission — only users who have a completed order containing the product can submit a review. Gracefully degrade to authenticated-user-only if order history tables are not yet available.

**Rationale**: The spec resolves this by requiring purchase verification as the default with a fallback. This prevents fake reviews while not blocking development if the orders feature is built later.

**Implementation notes**:
- Review submission endpoint checks for an order with status `delivered` or `paid` containing the product.
- If the orders/order_items tables don't exist yet (migration not run), fall back to allowing any authenticated user.
- The check is implemented in the review service layer, making it easy to tighten later.
- One review per user per product, enforced by a unique constraint on `(user_id, product_id)`.

## R-006: Category Tree Query Strategy

**Decision**: Use adjacency list with a single recursive query (CTE) to fetch the full tree. Cache the result since categories change infrequently.

**Rationale**: With max 2 levels of nesting and ~50 categories, a single recursive CTE is efficient and simple. No need for nested sets or materialized paths.

**Alternatives considered**:
- **Nested sets**: Efficient for reads but complex for inserts/updates. Overkill for 2 levels.
- **Materialized path**: Good for deep trees but unnecessary at 2 levels.
- **Multiple queries (one per level)**: Simpler code but more round trips.

**Implementation notes**:
- Category table has a nullable `parent_id` (self-referencing FK).
- A CHECK constraint or application-level validation enforces max 2 levels: a category with a `parent_id` cannot itself be a parent.
- The `GET /api/v1/categories` endpoint returns a nested JSON tree.
- Consider caching this response (e.g., TanStack Query `staleTime` on frontend, or a short TTL cache on backend) since categories change rarely.

## R-007: Price Storage and Display

**Decision**: Store all prices as integers in cents in the database. Format to human-readable currency strings on the frontend.

**Rationale**: Constitution Principle VI mandates integer (cents) storage. This avoids floating-point rounding errors in calculations (tax, discounts, totals).

**Implementation notes**:
- Database columns: `base_price INTEGER NOT NULL` (cents), `price_override INTEGER` (cents, nullable on variants).
- API returns prices as integers (cents).
- Frontend utility function: `formatPrice(cents: number): string` → e.g., `"$19.99"`.
- Filter parameters `min_price` and `max_price` also use cents.

## R-008: Soft Delete Strategy for Products

**Decision**: Use a `deleted_at` timestamp column. Soft-deleted products are excluded from all customer-facing queries by default.

**Rationale**: Constitution Principle VII requires soft deletes for user-facing data. Products may be referenced by historical orders, so hard deletion would break FK integrity.

**Implementation notes**:
- `deleted_at TIMESTAMP NULL DEFAULT NULL` on products table.
- All product queries include `WHERE deleted_at IS NULL` by default.
- Admin endpoints (spec 005) will handle soft deletion.
- SQLAlchemy query filter applied at the service layer or via a mixin.

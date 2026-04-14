# Research: Admin Dashboard

**Feature**: Admin Dashboard
**Date**: 2026-04-14

## R-001: Admin Authorization Pattern

**Decision**: Use a FastAPI dependency (`require_admin`) that checks the current user's role from the JWT token. All admin router files include this dependency at the router level so every endpoint is protected.

**Rationale**: The User entity already has a `role` field ('customer' or 'admin') from Spec 002. The JWT token already contains the user ID, and the existing `get_current_user` dependency resolves the User object. Adding a thin wrapper that checks `user.role == 'admin'` and raises 403 if not is the simplest approach. Router-level dependencies ensure no endpoint is accidentally left unprotected.

**Alternatives considered**:
- Decorator-based auth: More flexible but requires remembering to decorate each endpoint. Router-level dependency is safer (fail-closed).
- Separate admin JWT with different claims: Overcomplicated — the role is already on the User model.
- Middleware-based path check: Less granular, harder to test, mixes path routing with auth logic.

---

## R-002: Image Upload and Storage

**Decision**: Store images on the local filesystem in a `media/products/{product_id}/` directory. Serve them via a static files mount or a dedicated endpoint. Images are stored as-is (no processing). Metadata (filename, URL, alt_text, position) is stored in the existing ProductImage table.

**Rationale**: Local filesystem is the simplest approach for v1 — no external service dependencies. The constitution requires `.env`-based configuration (Principle IX), so the media directory path is configurable. Cloud storage (S3/R2) can be added later by swapping the storage backend.

**Alternatives considered**:
- S3/R2 cloud storage: Better for production scale, but adds infrastructure dependency for v1.
- Database BLOB storage: Poor performance for images, not suitable.
- Base64 in database: Inflates database size, very poor practice.

**Implementation pattern**:
1. Upload endpoint accepts multipart form data.
2. Validate file type (JPEG, PNG, WebP) and size (≤ 5MB).
3. Generate a UUID filename to avoid collisions.
4. Save to `MEDIA_ROOT/products/{product_id}/{uuid}.{ext}`.
5. Create ProductImage record with URL pointing to `/media/products/{product_id}/{uuid}.{ext}`.
6. Serve static files from `MEDIA_ROOT` via a mounted static files directory.

---

## R-003: Rich Text Editor for Product Description

**Decision**: Use a markdown-based editor on the frontend. Store product descriptions as markdown in the database. Render on the storefront using a markdown-to-HTML library.

**Rationale**: Markdown is simpler than full WYSIWYG HTML, safer (no XSS from arbitrary HTML), and aligns with the existing `description TEXT` field. Many lightweight React markdown editors exist (e.g., react-md-editor or similar shadcn-compatible components). The constitution doesn't mandate a specific editor, so choosing the simplest option that integrates with shadcn/ui.

**Alternatives considered**:
- Full WYSIWYG (TinyMCE, CKEditor, Tiptap): More feature-rich but heavier, potential XSS if HTML is stored directly.
- Plain text only: Too limiting for product descriptions (no formatting, lists, bold, etc.).

---

## R-004: Dashboard Analytics Caching

**Decision**: Cache dashboard statistics server-side using an in-memory cache with a 5-minute TTL. The cache key includes the time range parameter (7/30/90 days). On cache miss, the backend runs aggregate queries and stores the result.

**Rationale**: Dashboard queries aggregate across orders, users, and products — potentially expensive on larger datasets. A 5-minute cache is a reasonable balance between data freshness and query load. In-memory caching (Python dict with TTL or `cachetools`) avoids adding Redis as a dependency for v1.

**Alternatives considered**:
- Redis cache: More robust but adds infrastructure dependency. Appropriate for v2 if scale demands it.
- Materialized database views: More complex to manage, requires refresh triggers.
- No caching: Risky — dashboard is the admin landing page, loaded frequently.
- Pre-computed table: Requires a background job to keep in sync, overcomplicated for v1.

**Implementation pattern**:
- Use `cachetools.TTLCache` or a simple dict with timestamp checking.
- Cache key: `dashboard_stats_{days}` where days is 7, 30, or 90.
- On cache miss: run aggregate queries, store result with timestamp.
- Return cached result if within TTL (5 minutes).

---

## R-005: Product Slug Auto-Generation

**Decision**: Auto-generate slugs from product name using: lowercase, replace spaces with hyphens, strip special characters, truncate to 255 chars. On conflict, append `-2`, `-3`, etc. by querying for existing slugs with the same prefix.

**Rationale**: The Product model already has a `slug` field (unique, from Spec 001). Auto-generation improves admin UX (no need to manually create URL-friendly strings). Conflict resolution ensures uniqueness without admin intervention.

**Implementation pattern**:
1. `base_slug = slugify(name)` — lowercase, hyphens, alphanumeric only.
2. Check if `base_slug` exists in the database.
3. If not, use it. If yes, query for `slug LIKE '{base_slug}-%'`, find the highest suffix, and use `{base_slug}-{n+1}`.
4. The slug field is editable by the admin (the auto-generated value is a default).

---

## R-006: Admin Refund from Order Management

**Decision**: Reuse the `refund_service.create_refund()` from Spec 004. The admin order management endpoint calls the same service. The difference from customer-initiated cancellation is that the admin can refund from any paid status, not just "paid" or "processing".

**Rationale**: The refund logic is identical — create a Stripe refund using the PaymentIntent ID. Centralizing in `refund_service` avoids duplication. Admin refunds update the order status to "refunded" (a payment_status, distinct from the order status "cancelled").

**Alternatives considered**:
- Separate admin refund service: Would duplicate logic. Reuse is better.
- Different refund statuses for admin vs customer: Unnecessary — a refund is a refund regardless of who initiated it.

---

## R-007: Last Admin Protection

**Decision**: Before demoting or deactivating an admin user, count the number of active admin users. If the count would drop to zero, reject the action with a clear error.

**Rationale**: This prevents a lockout scenario where no admin can access the dashboard. The check is simple: `SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = true`. If count is 1 and the target user is that admin, reject.

**Implementation pattern**:
- In user_service or admin_user_service, before role change or deactivation:
  - If target user is admin AND (new_role != 'admin' OR is_active = false):
    - Count active admins. If count == 1, raise error "Cannot remove the last admin."

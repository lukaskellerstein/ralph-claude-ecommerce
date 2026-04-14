# Quickstart: Admin Dashboard

**Feature**: Admin Dashboard
**Date**: 2026-04-14

## Prerequisites

- Specs 001-004 must be implemented.
- An admin user must exist (seeded or created via CLI).
- Stripe configured for refunds (same as Spec 003/004).

## Environment Variables

Add to `.env`:

```env
# Media storage
MEDIA_ROOT=./media
MAX_IMAGE_SIZE_MB=5
MAX_IMAGES_PER_PRODUCT=10
ACCEPTED_IMAGE_TYPES=image/jpeg,image/png,image/webp

# Dashboard cache
DASHBOARD_CACHE_TTL_SECONDS=300
```

## Backend Setup

1. Install new dependencies (if needed):
   ```bash
   pip install python-multipart cachetools
   ```
   Note: `python-multipart` is likely already installed via FastAPI. `cachetools` provides TTL cache.

2. No new database migration needed — this feature uses existing tables.

3. Create media directory:
   ```bash
   mkdir -p media/products
   ```

4. New files to create:
   - `backend/app/core/admin_deps.py` — `require_admin` dependency
   - `backend/app/services/admin_product_service.py` — Product CRUD, image management, variant management
   - `backend/app/services/admin_category_service.py` — Category CRUD with tree management
   - `backend/app/services/admin_order_service.py` — Order listing, status management, admin refunds
   - `backend/app/services/admin_user_service.py` — User listing, role/status management
   - `backend/app/services/dashboard_service.py` — Analytics aggregation with caching
   - `backend/app/schemas/admin.py` — Admin-specific Pydantic schemas
   - `backend/app/api/v1/admin/products.py` — Admin product endpoints
   - `backend/app/api/v1/admin/categories.py` — Admin category endpoints
   - `backend/app/api/v1/admin/orders.py` — Admin order endpoints
   - `backend/app/api/v1/admin/users.py` — Admin user endpoints
   - `backend/app/api/v1/admin/dashboard.py` — Dashboard stats endpoint

5. Mount static file serving for media in `backend/app/main.py`.
6. Register admin routers with `/api/v1/admin` prefix.

## Frontend Setup

1. Install rich text editor (if not already available):
   ```bash
   cd frontend
   npm install @uiw/react-md-editor
   ```

2. Install chart library:
   ```bash
   npm install recharts
   ```

3. New files to create:
   - `frontend/src/pages/admin/dashboard.tsx` — Analytics dashboard
   - `frontend/src/pages/admin/products.tsx` — Product list
   - `frontend/src/pages/admin/product-form.tsx` — Create/edit product
   - `frontend/src/pages/admin/categories.tsx` — Category tree management
   - `frontend/src/pages/admin/orders.tsx` — Order list
   - `frontend/src/pages/admin/order-detail.tsx` — Admin order detail
   - `frontend/src/pages/admin/users.tsx` — User management
   - `frontend/src/components/admin/admin-layout.tsx` — Admin sidebar layout
   - `frontend/src/components/admin/admin-guard.tsx` — Route guard for admin role
   - `frontend/src/components/admin/data-table.tsx` — Reusable data table with search/filter/sort/pagination
   - `frontend/src/components/admin/image-upload.tsx` — Image upload with drag-and-drop reorder
   - `frontend/src/components/admin/variant-manager.tsx` — Add/edit/remove variants
   - `frontend/src/components/admin/kpi-card.tsx` — KPI summary card
   - `frontend/src/components/admin/revenue-chart.tsx` — Daily revenue chart
   - `frontend/src/components/admin/category-tree.tsx` — Tree view with drag-and-drop
   - `frontend/src/hooks/use-admin-products.ts` — Admin product API hooks
   - `frontend/src/hooks/use-admin-categories.ts` — Admin category API hooks
   - `frontend/src/hooks/use-admin-orders.ts` — Admin order API hooks
   - `frontend/src/hooks/use-admin-users.ts` — Admin user API hooks
   - `frontend/src/hooks/use-admin-dashboard.ts` — Dashboard stats hook

4. Add admin routes in `frontend/src/App.tsx` under `/admin/*` with admin guard.

## Seeding an Admin User

```bash
# Option: direct database insert
psql -d ecommerce -c "UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';"

# Or create a management command
python -m app.cli.create_admin --email admin@example.com --password AdminPass123
```

## Testing

```bash
# Backend
cd backend
pytest tests/test_admin_products.py tests/test_admin_categories.py tests/test_admin_orders.py tests/test_admin_users.py tests/test_admin_dashboard.py -v

# Frontend
cd frontend
npm test -- --run tests/admin/
```

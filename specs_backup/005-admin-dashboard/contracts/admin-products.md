# API Contract: Admin Products

All endpoints require authentication with `role = admin`. Returns 403 for non-admin users.

## GET /api/v1/admin/products

List all products with search, filtering, sorting, and pagination.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | No | Search by product name |
| category_id | UUID | No | Filter by category |
| status | string | No | Filter by status: 'active' or 'inactive' |
| sort | string | No | Sort by: `name_asc`, `name_desc`, `price_asc`, `price_desc`, `newest`, `oldest`. Default: `newest` |
| after | string | No | Cursor for pagination |
| page_size | integer | No | Items per page (1-100). Default: 25 |

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "slug": "string",
      "category": { "id": "uuid", "name": "string" },
      "base_price": 1999,
      "total_stock": 42,
      "is_active": true,
      "primary_image": { "url": "string", "alt_text": "string" },
      "variant_count": 3,
      "created_at": "2026-04-14T10:00:00Z"
    }
  ],
  "next_cursor": "string | null",
  "has_next_page": true,
  "total_count": 150
}
```

---

## POST /api/v1/admin/products

Create a new product.

### Request Body

```json
{
  "name": "string (1-255 chars, required)",
  "slug": "string (optional, auto-generated from name if omitted)",
  "description": "string (markdown, required)",
  "category_id": "uuid (required)",
  "base_price": 1999,
  "is_active": true
}
```

### Response 201

```json
{
  "id": "uuid",
  "name": "string",
  "slug": "string",
  "description": "string",
  "category": { "id": "uuid", "name": "string" },
  "base_price": 1999,
  "is_active": true,
  "images": [],
  "variants": [],
  "created_at": "2026-04-14T10:00:00Z"
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 403 | FORBIDDEN | Not an admin user |
| 404 | CATEGORY_NOT_FOUND | Category does not exist |
| 422 | VALIDATION_ERROR | Invalid request body |

---

## PATCH /api/v1/admin/products/{product_id}

Update a product's fields.

### Request Body (all optional)

```json
{
  "name": "string",
  "slug": "string",
  "description": "string",
  "category_id": "uuid",
  "base_price": 1999,
  "is_active": false
}
```

### Response 200

Full product object (same as POST response).

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 403 | FORBIDDEN | Not an admin user |
| 404 | PRODUCT_NOT_FOUND | Product does not exist |
| 409 | SLUG_CONFLICT | Slug already in use by another product |
| 422 | VALIDATION_ERROR | Invalid request body |

---

## POST /api/v1/admin/products/{product_id}/images

Upload an image for a product. Multipart form data.

### Request Body (multipart/form-data)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | Image file (JPEG, PNG, WebP, max 5MB) |
| alt_text | string | No | Alt text for the image. Default: "" |
| position | integer | No | Display position. Default: append to end |

### Response 201

```json
{
  "id": "uuid",
  "url": "/media/products/{product_id}/{uuid}.jpg",
  "alt_text": "string",
  "position": 3
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | INVALID_FILE_TYPE | Accepted formats: JPEG, PNG, WebP |
| 400 | FILE_TOO_LARGE | Maximum file size is 5MB |
| 400 | TOO_MANY_IMAGES | Maximum 10 images per product |
| 403 | FORBIDDEN | Not an admin user |
| 404 | PRODUCT_NOT_FOUND | Product does not exist |

---

## PATCH /api/v1/admin/products/{product_id}/images/{image_id}

Update image metadata (alt_text, position).

### Request Body

```json
{
  "alt_text": "string (optional)",
  "position": 2
}
```

### Response 200

Updated image object.

---

## DELETE /api/v1/admin/products/{product_id}/images/{image_id}

Delete an image. Removes file from filesystem and database record.

### Response 200

```json
{ "detail": "Image deleted" }
```

---

## POST /api/v1/admin/products/{product_id}/variants

Add a variant to a product.

### Request Body

```json
{
  "variant_type": "string (e.g., 'Size', required)",
  "variant_value": "string (e.g., 'Large', required)",
  "sku": "string (unique, required)",
  "price_override": 2499,
  "stock_quantity": 10
}
```

### Response 201

Variant object.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 403 | FORBIDDEN | Not an admin user |
| 404 | PRODUCT_NOT_FOUND | Product does not exist |
| 409 | SKU_CONFLICT | SKU already in use |
| 422 | VALIDATION_ERROR | Invalid request body |

---

## PATCH /api/v1/admin/products/{product_id}/variants/{variant_id}

Update a variant's fields.

### Request Body (all optional)

```json
{
  "variant_type": "string",
  "variant_value": "string",
  "sku": "string",
  "price_override": 2499,
  "stock_quantity": 20
}
```

### Response 200

Updated variant object.

---

## DELETE /api/v1/admin/products/{product_id}/variants/{variant_id}

Delete a variant. Hard delete.

### Response 200

```json
{ "detail": "Variant deleted" }
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | VARIANT_IN_ORDERS | Cannot delete variant referenced by existing orders |
| 403 | FORBIDDEN | Not an admin user |
| 404 | VARIANT_NOT_FOUND | Variant does not exist |

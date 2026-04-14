# API Contract: Wishlist

## GET /api/v1/users/me/wishlist

List all products on the current user's wishlist. Requires authentication.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| after | string | No | Cursor token for pagination |
| page_size | integer | No | Items per page (1-50). Default: 20 |

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "product": {
        "id": "uuid",
        "name": "string",
        "slug": "string",
        "base_price": 1999,
        "primary_image": {
          "url": "string",
          "alt_text": "string"
        },
        "has_stock": true,
        "is_active": true
      },
      "created_at": "2026-04-14T10:00:00Z"
    }
  ],
  "next_cursor": "string | null",
  "has_next_page": true
}
```

**Note**: Products that have been soft-deleted will have `is_active: false` and should be displayed with a "No longer available" label.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |

---

## POST /api/v1/users/me/wishlist

Add a product to the wishlist. If the product is already wishlisted, this is a no-op (returns 200, not 409). Requires authentication.

### Request Body

```json
{
  "product_id": "uuid (required)"
}
```

### Response 200

```json
{
  "id": "uuid",
  "product_id": "uuid",
  "created_at": "2026-04-14T10:00:00Z"
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | PRODUCT_NOT_FOUND | Product does not exist |

---

## DELETE /api/v1/users/me/wishlist/{product_id}

Remove a product from the wishlist. Requires authentication.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| product_id | UUID | Product to remove from wishlist |

### Response 200

```json
{
  "detail": "Removed from wishlist"
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | WISHLIST_ITEM_NOT_FOUND | Product is not in the wishlist |

---

## GET /api/v1/users/me/wishlist/check

Check if specific products are in the wishlist. Useful for rendering wishlist icons on product cards without fetching the full wishlist. Requires authentication.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| product_ids | string | Yes | Comma-separated list of product UUIDs (max 50) |

### Response 200

```json
{
  "wishlisted": ["uuid1", "uuid3"]
}
```

Returns only the product IDs that are in the wishlist.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | INVALID_REQUEST | Too many product IDs (max 50) |
| 401 | NOT_AUTHENTICATED | Not authenticated |

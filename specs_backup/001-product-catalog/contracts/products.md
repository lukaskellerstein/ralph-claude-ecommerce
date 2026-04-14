# API Contract: Products

## GET /api/v1/products

List products with filtering, sorting, search, and cursor-based pagination.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category_id | UUID | No | Filter by category |
| q | string | No | Full-text search query |
| min_price | integer | No | Minimum price in cents |
| max_price | integer | No | Maximum price in cents |
| min_rating | integer (1-5) | No | Minimum average rating |
| in_stock | boolean | No | If true, only show products with stock > 0 |
| sort | string | No | One of: `price_asc`, `price_desc`, `newest`, `popular`. Default: `newest` |
| after | string | No | Cursor token for pagination |
| page_size | integer | No | Items per page (1-100). Default: 20 |

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "slug": "string",
      "description": "string (truncated to 200 chars)",
      "base_price": 1999,
      "category": {
        "id": "uuid",
        "name": "string",
        "slug": "string"
      },
      "primary_image": {
        "url": "string",
        "alt_text": "string"
      },
      "average_rating": 4.5,
      "review_count": 42,
      "has_stock": true
    }
  ],
  "next_cursor": "string | null",
  "has_next_page": true
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | INVALID_FILTER | Invalid filter parameter value |
| 400 | INVALID_CURSOR | Malformed pagination cursor |

---

## GET /api/v1/products/{slug}

Get full product details by slug.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| slug | string | Product URL slug |

### Response 200

```json
{
  "id": "uuid",
  "name": "string",
  "slug": "string",
  "description": "string (full markdown/rich text)",
  "base_price": 1999,
  "category": {
    "id": "uuid",
    "name": "string",
    "slug": "string",
    "parent": {
      "id": "uuid",
      "name": "string",
      "slug": "string"
    }
  },
  "images": [
    {
      "id": "uuid",
      "url": "string",
      "alt_text": "string",
      "position": 0
    }
  ],
  "variants": [
    {
      "id": "uuid",
      "variant_type": "Size",
      "variant_value": "Large",
      "sku": "string",
      "price": 2499,
      "stock_quantity": 10,
      "in_stock": true
    }
  ],
  "average_rating": 4.5,
  "review_count": 42,
  "rating_distribution": {
    "1": 2,
    "2": 3,
    "3": 5,
    "4": 12,
    "5": 20
  },
  "created_at": "2026-04-14T10:00:00Z"
}
```

**Note**: Variant `price` field returns `price_override` if set, otherwise `base_price`.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 404 | PRODUCT_NOT_FOUND | Product with this slug does not exist |

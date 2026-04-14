# API Contract: Reviews

## GET /api/v1/products/{slug}/reviews

List reviews for a product with cursor-based pagination.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| slug | string | Product URL slug |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| after | string | No | Cursor token for pagination |
| page_size | integer | No | Items per page (1-50). Default: 10 |

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "rating": 5,
      "text": "string",
      "reviewer_name": "string",
      "created_at": "2026-04-14T10:00:00Z"
    }
  ],
  "next_cursor": "string | null",
  "has_next_page": true
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 404 | PRODUCT_NOT_FOUND | Product with this slug does not exist |
| 400 | INVALID_CURSOR | Malformed pagination cursor |

---

## POST /api/v1/products/{slug}/reviews

Submit a review for a product. Requires authentication. User must have purchased the product (graceful fallback to authenticated-only if order system unavailable).

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| slug | string | Product URL slug |

### Authentication

Required. JWT via httpOnly cookie.

### Request Body

```json
{
  "rating": 5,
  "text": "string (1-5000 characters)"
}
```

### Validation

| Field | Rule |
|-------|------|
| rating | Required, integer, 1-5 |
| text | Required, string, 1-5000 characters |

### Response 201

```json
{
  "id": "uuid",
  "rating": 5,
  "text": "string",
  "reviewer_name": "string",
  "created_at": "2026-04-14T10:00:00Z"
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | UNAUTHORIZED | Authentication required |
| 403 | PURCHASE_REQUIRED | User has not purchased this product |
| 404 | PRODUCT_NOT_FOUND | Product with this slug does not exist |
| 409 | REVIEW_EXISTS | User has already reviewed this product |
| 422 | VALIDATION_ERROR | Invalid request body |

---

## PUT /api/v1/products/{slug}/reviews/{review_id}

Update an existing review. Only the review author can update.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| slug | string | Product URL slug |
| review_id | UUID | Review identifier |

### Authentication

Required. JWT via httpOnly cookie.

### Request Body

```json
{
  "rating": 4,
  "text": "string (1-5000 characters)"
}
```

### Response 200

```json
{
  "id": "uuid",
  "rating": 4,
  "text": "string",
  "reviewer_name": "string",
  "created_at": "2026-04-14T10:00:00Z",
  "updated_at": "2026-04-14T12:00:00Z"
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | User is not the review author |
| 404 | REVIEW_NOT_FOUND | Review does not exist |
| 422 | VALIDATION_ERROR | Invalid request body |

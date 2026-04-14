# API Contract: Admin Categories

All endpoints require authentication with `role = admin`. Returns 403 for non-admin users.

## GET /api/v1/admin/categories

List all categories as a tree structure.

### Response 200

```json
{
  "categories": [
    {
      "id": "uuid",
      "name": "string",
      "slug": "string",
      "position": 0,
      "product_count": 15,
      "children": [
        {
          "id": "uuid",
          "name": "string",
          "slug": "string",
          "position": 0,
          "product_count": 8,
          "children": []
        }
      ]
    }
  ]
}
```

---

## POST /api/v1/admin/categories

Create a new category.

### Request Body

```json
{
  "name": "string (1-100 chars, required)",
  "slug": "string (optional, auto-generated from name)",
  "parent_id": "uuid (optional, null for root category)",
  "position": 0
}
```

### Response 201

Category object.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | MAX_NESTING_EXCEEDED | Categories cannot be nested more than 2 levels |
| 403 | FORBIDDEN | Not an admin user |
| 404 | PARENT_NOT_FOUND | Parent category does not exist |
| 409 | SLUG_CONFLICT | Slug already in use |

---

## PATCH /api/v1/admin/categories/{category_id}

Update a category.

### Request Body (all optional)

```json
{
  "name": "string",
  "slug": "string",
  "parent_id": "uuid | null",
  "position": 1
}
```

### Response 200

Updated category object.

---

## DELETE /api/v1/admin/categories/{category_id}

Delete a category. Blocked if products or subcategories are assigned.

### Response 200

```json
{ "detail": "Category deleted" }
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | HAS_PRODUCTS | Cannot delete category with assigned products. Reassign products first. |
| 400 | HAS_SUBCATEGORIES | Cannot delete category with subcategories. Delete subcategories first. |
| 403 | FORBIDDEN | Not an admin user |
| 404 | CATEGORY_NOT_FOUND | Category does not exist |

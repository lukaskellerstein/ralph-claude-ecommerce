# API Contract: Categories

## GET /api/v1/categories

Get the full category tree (max 2 levels deep).

### Query Parameters

None.

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Electronics",
      "slug": "electronics",
      "product_count": 45,
      "children": [
        {
          "id": "uuid",
          "name": "Laptops",
          "slug": "laptops",
          "product_count": 18,
          "children": []
        },
        {
          "id": "uuid",
          "name": "Phones",
          "slug": "phones",
          "product_count": 27,
          "children": []
        }
      ]
    },
    {
      "id": "uuid",
      "name": "Clothing",
      "slug": "clothing",
      "product_count": 120,
      "children": []
    }
  ]
}
```

**Notes**:
- Returns all categories in a nested tree structure.
- `product_count` includes only active, non-deleted products.
- `children` is always an array (empty for leaf categories).
- Root categories have no parent; children have exactly one parent.

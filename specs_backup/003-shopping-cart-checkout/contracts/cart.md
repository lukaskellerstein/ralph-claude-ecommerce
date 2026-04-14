# API Contract: Cart

## GET /api/v1/cart

Get the current user's cart with all items. Requires authentication.

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "variant_id": "uuid | null",
      "quantity": 2,
      "product": {
        "id": "uuid",
        "name": "string",
        "slug": "string",
        "base_price": 1999,
        "primary_image": {
          "url": "string",
          "alt_text": "string"
        },
        "is_active": true
      },
      "variant": {
        "id": "uuid",
        "variant_type": "Size",
        "variant_value": "Large",
        "sku": "string",
        "price": 2499,
        "stock_quantity": 10,
        "in_stock": true
      },
      "unit_price": 2499,
      "line_total": 4998,
      "created_at": "2026-04-14T10:00:00Z",
      "updated_at": "2026-04-14T10:05:00Z"
    }
  ],
  "item_count": 2,
  "subtotal": 4998
}
```

**Note**: `unit_price` returns the variant's `price_override` if set, otherwise the product's `base_price`. `line_total` = `unit_price * quantity`.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |

---

## POST /api/v1/cart/items

Add an item to the cart. If the same product+variant is already in the cart, increments quantity. Requires authentication.

### Request Body

```json
{
  "product_id": "uuid (required)",
  "variant_id": "uuid | null (required if product has variants)",
  "quantity": 1
}
```

**Note**: `quantity` defaults to 1 if omitted.

### Response 201

Returns the updated cart (same format as GET /api/v1/cart).

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | VARIANT_REQUIRED | This product has variants; variant_id is required |
| 400 | OUT_OF_STOCK | Insufficient stock for this item |
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | PRODUCT_NOT_FOUND | Product does not exist or is inactive |
| 404 | VARIANT_NOT_FOUND | Variant does not exist |

---

## PATCH /api/v1/cart/items/{item_id}

Update the quantity of a cart item. Requires authentication.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| item_id | UUID | Cart item ID |

### Request Body

```json
{
  "quantity": 3
}
```

### Response 200

Returns the updated cart (same format as GET /api/v1/cart).

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | INVALID_QUANTITY | Quantity must be greater than 0 |
| 400 | OUT_OF_STOCK | Insufficient stock for requested quantity |
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | CART_ITEM_NOT_FOUND | Cart item does not exist or does not belong to this user |

---

## DELETE /api/v1/cart/items/{item_id}

Remove an item from the cart. Requires authentication.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| item_id | UUID | Cart item ID |

### Response 200

Returns the updated cart (same format as GET /api/v1/cart).

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | CART_ITEM_NOT_FOUND | Cart item does not exist or does not belong to this user |

---

## POST /api/v1/cart/merge

Merge guest cart items into the authenticated user's server-side cart. Requires authentication.

### Request Body

```json
{
  "items": [
    {
      "product_id": "uuid",
      "variant_id": "uuid | null",
      "quantity": 2
    }
  ]
}
```

### Response 200

Returns the merged cart (same format as GET /api/v1/cart).

### Merge Logic

For each guest item:
- If the same product+variant exists in the server cart: keep `MAX(server_quantity, guest_quantity)`.
- If it does not exist: add the item to the server cart.
- Items referencing inactive/deleted products or out-of-stock variants are silently skipped.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 422 | VALIDATION_ERROR | Invalid request body |

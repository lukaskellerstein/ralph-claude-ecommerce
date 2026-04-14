# API Contract: Orders

## GET /api/v1/orders

List the current user's orders with cursor-based pagination. Requires authentication.

*Note: This endpoint was introduced in Spec 003. This contract documents the complete behavior including enhancements from Spec 004.*

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by order status (e.g., "paid", "shipped") |
| after | string | No | Cursor token for pagination |
| page_size | integer | No | Items per page (1-50). Default: 10 |

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "order_number": "ORD-20260414-00042",
      "status": "paid",
      "payment_status": "succeeded",
      "item_count": 3,
      "total": 6048,
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
| 401 | NOT_AUTHENTICATED | Not authenticated |

---

## GET /api/v1/orders/{order_number}

Get full order details by order number. Requires authentication. Users can only access their own orders.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| order_number | string | Human-readable order number (e.g., ORD-20260414-00042) |

### Response 200

```json
{
  "id": "uuid",
  "order_number": "ORD-20260414-00042",
  "status": "paid",
  "payment_status": "succeeded",
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "product_name": "string",
      "variant_type": "Size",
      "variant_value": "Large",
      "sku": "string",
      "unit_price": 2499,
      "quantity": 2,
      "line_total": 4998
    }
  ],
  "shipping_address": {
    "label": "string",
    "street_line_1": "string",
    "street_line_2": "string | null",
    "city": "string",
    "state": "string",
    "postal_code": "string",
    "country": "string"
  },
  "shipping_method": "standard",
  "shipping_cost": 0,
  "subtotal": 4998,
  "tax_amount": 1050,
  "total": 6048,
  "tracking_number": "string | null",
  "estimated_delivery_date": "2026-04-21",
  "cancelled_at": "string | null",
  "status_history": [
    {
      "previous_status": null,
      "new_status": "pending",
      "actor_type": "system",
      "note": null,
      "created_at": "2026-04-14T10:00:00Z"
    },
    {
      "previous_status": "pending",
      "new_status": "paid",
      "actor_type": "system",
      "note": null,
      "created_at": "2026-04-14T10:00:05Z"
    }
  ],
  "can_cancel": true,
  "created_at": "2026-04-14T10:00:00Z"
}
```

**Note**: `can_cancel` is true when status is "paid" or "processing" and the requesting user is the order owner.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | ORDER_NOT_FOUND | Order does not exist or does not belong to this user |

---

## POST /api/v1/orders/{order_number}/cancel

Cancel an order and initiate a full refund. Requires authentication. Only works when order status is "paid" or "processing".

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| order_number | string | Human-readable order number |

### Request Body

```json
{
  "reason": "string (optional, max 500 chars)"
}
```

### Response 200

```json
{
  "id": "uuid",
  "order_number": "ORD-20260414-00042",
  "status": "cancelled",
  "payment_status": "refunded",
  "cancelled_at": "2026-04-14T12:00:00Z",
  "refund_status": "succeeded"
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | CANNOT_CANCEL | Order cannot be cancelled in its current status |
| 400 | REFUND_FAILED | Refund could not be processed. Contact support. |
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | ORDER_NOT_FOUND | Order does not exist or does not belong to this user |

---

## POST /api/v1/orders/{order_number}/reorder

Add all available items from a past order to the current cart. Requires authentication.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| order_number | string | Human-readable order number |

### Response 200

```json
{
  "added_items": [
    {
      "product_id": "uuid",
      "product_name": "string",
      "variant_id": "uuid | null",
      "quantity": 2
    }
  ],
  "unavailable_items": [
    {
      "product_id": "uuid",
      "product_name": "string",
      "reason": "out_of_stock | product_deleted | variant_unavailable"
    }
  ]
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | ORDER_NOT_FOUND | Order does not exist or does not belong to this user |

---

## Order Status Color Mapping

For frontend display:

| Status | Color | CSS Class Suggestion |
|--------|-------|---------------------|
| pending | Yellow | `bg-yellow-100 text-yellow-800` |
| paid | Blue | `bg-blue-100 text-blue-800` |
| processing | Blue | `bg-blue-100 text-blue-800` |
| shipped | Purple | `bg-purple-100 text-purple-800` |
| delivered | Green | `bg-green-100 text-green-800` |
| cancelled | Red | `bg-red-100 text-red-800` |
| refunded | Gray | `bg-gray-100 text-gray-800` |

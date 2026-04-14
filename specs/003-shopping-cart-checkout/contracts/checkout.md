# API Contract: Checkout

## POST /api/v1/checkout

Create an order from the current cart. Validates stock, calculates totals, creates a Stripe PaymentIntent, and returns the client secret for payment confirmation. Requires authentication.

### Request Body

```json
{
  "shipping_address_id": "uuid (use existing saved address)",
  "shipping_address": {
    "label": "string (1-50 chars)",
    "street_line_1": "string (1-255 chars, required)",
    "street_line_2": "string (optional)",
    "city": "string (1-100 chars, required)",
    "state": "string (1-100 chars, required)",
    "postal_code": "string (1-20 chars, required)",
    "country": "string (1-100 chars, required)"
  },
  "save_address": false,
  "shipping_method": "standard"
}
```

**Note**: Provide either `shipping_address_id` (to use a saved address) OR `shipping_address` (to enter a new one), not both. If `save_address` is true and `shipping_address` is provided, the address is saved to the user's profile.

### Response 201

```json
{
  "order": {
    "id": "uuid",
    "order_number": "ORD-20260414-00042",
    "status": "pending",
    "payment_status": "pending",
    "items": [
      {
        "id": "uuid",
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
    "estimated_delivery_date": "2026-04-21",
    "created_at": "2026-04-14T10:00:00Z"
  },
  "payment": {
    "client_secret": "pi_xxx_secret_xxx",
    "amount": 6048,
    "currency": "eur"
  }
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | CART_EMPTY | Cart is empty |
| 400 | OUT_OF_STOCK | One or more items exceed available stock |
| 400 | INVALID_SHIPPING_METHOD | Shipping method must be 'standard' or 'express' |
| 400 | ADDRESS_REQUIRED | Either shipping_address_id or shipping_address is required |
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | ADDRESS_NOT_FOUND | Saved address does not exist or does not belong to this user |
| 422 | VALIDATION_ERROR | Invalid request body |

**Out of stock response detail** (when code is `OUT_OF_STOCK`):

```json
{
  "detail": "One or more items exceed available stock",
  "code": "OUT_OF_STOCK",
  "affected_items": [
    {
      "product_id": "uuid",
      "variant_id": "uuid | null",
      "product_name": "string",
      "requested_quantity": 5,
      "available_quantity": 2
    }
  ]
}
```

---

## POST /api/v1/checkout/confirm

Confirm that payment was successful (client-side fallback). Called by the frontend after Stripe.js confirms the payment. The authoritative confirmation is the webhook, but this endpoint provides immediate UX feedback. Requires authentication.

### Request Body

```json
{
  "order_id": "uuid (required)",
  "payment_intent_id": "string (required)"
}
```

### Response 200

```json
{
  "order": {
    "id": "uuid",
    "order_number": "ORD-20260414-00042",
    "status": "paid",
    "payment_status": "succeeded",
    "items": [...],
    "shipping_address": {...},
    "shipping_method": "standard",
    "shipping_cost": 0,
    "subtotal": 4998,
    "tax_amount": 1050,
    "total": 6048,
    "estimated_delivery_date": "2026-04-21",
    "created_at": "2026-04-14T10:00:00Z"
  }
}
```

**Note**: This endpoint verifies the PaymentIntent status with Stripe before updating the order. If the PaymentIntent is not yet `succeeded`, it returns the order in its current state without modifying it (the webhook will handle the update).

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | PAYMENT_MISMATCH | Payment intent does not match this order |
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | ORDER_NOT_FOUND | Order does not exist or does not belong to this user |

---

## POST /api/v1/webhooks/stripe

Handle Stripe webhook events. No authentication required (verified by Stripe signature).

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| stripe-signature | Yes | Stripe webhook signature for verification |

### Request Body

Raw Stripe event JSON (parsed by Stripe SDK).

### Handled Events

| Event | Action |
|-------|--------|
| `payment_intent.succeeded` | Update order `payment_status` → `succeeded`, `status` → `paid`. Decrement stock. Clear cart. |
| `payment_intent.payment_failed` | Update order `payment_status` → `failed`, `status` → `cancelled`. |

### Response 200

```json
{
  "received": true
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | INVALID_SIGNATURE | Webhook signature verification failed |

---

## GET /api/v1/orders

List the current user's orders with cursor-based pagination. Requires authentication.

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

## GET /api/v1/orders/{order_id}

Get full order details. Requires authentication (user can only view their own orders).

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| order_id | UUID | Order ID |

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
  "estimated_delivery_date": "2026-04-21",
  "created_at": "2026-04-14T10:00:00Z"
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |
| 404 | ORDER_NOT_FOUND | Order does not exist or does not belong to this user |

---

## Shipping Configuration

Shipping options are hardcoded for v1:

| Method | Name | Delivery Window | Cost (cents) | Free Threshold (cents) |
|--------|------|-----------------|--------------|----------------------|
| standard | Standard Shipping | 5-7 business days | 599 | 10000 (free above) |
| express | Express Shipping | 2-3 business days | 1499 | N/A (always charged) |

These values are configurable via environment variables.

# API Contract: Admin Orders

All endpoints require authentication with `role = admin`. Returns 403 for non-admin users.

## GET /api/v1/admin/orders

List all orders across all customers with filtering and pagination.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Comma-separated status filter (e.g., "paid,processing") |
| date_from | date | No | Filter orders placed on or after this date (YYYY-MM-DD) |
| date_to | date | No | Filter orders placed on or before this date (YYYY-MM-DD) |
| q | string | No | Search by order number or customer name/email |
| after | string | No | Cursor for pagination |
| page_size | integer | No | Items per page (1-100). Default: 25 |

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "order_number": "ORD-20260414-00042",
      "customer": {
        "id": "uuid",
        "email": "string",
        "first_name": "string",
        "last_name": "string"
      },
      "total": 6048,
      "status": "paid",
      "payment_status": "succeeded",
      "item_count": 3,
      "created_at": "2026-04-14T10:00:00Z"
    }
  ],
  "next_cursor": "string | null",
  "has_next_page": true,
  "total_count": 500
}
```

---

## GET /api/v1/admin/orders/{order_id}

Get full order details (admin view). Same as customer order detail but with additional admin fields.

### Response 200

```json
{
  "id": "uuid",
  "order_number": "ORD-20260414-00042",
  "customer": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string"
  },
  "status": "paid",
  "payment_status": "succeeded",
  "items": [...],
  "shipping_address": {...},
  "shipping_method": "standard",
  "shipping_cost": 0,
  "subtotal": 4998,
  "tax_amount": 1050,
  "total": 6048,
  "tracking_number": "string | null",
  "admin_notes": "string | null",
  "status_history": [...],
  "valid_transitions": ["processing", "cancelled"],
  "can_refund": true,
  "created_at": "2026-04-14T10:00:00Z"
}
```

**Note**: `valid_transitions` lists the statuses the admin can transition to from the current status. `can_refund` is true when payment_status is "succeeded" and order hasn't been refunded.

---

## PATCH /api/v1/admin/orders/{order_id}/status

Update an order's status. Validates against the status state machine.

### Request Body

```json
{
  "status": "processing",
  "tracking_number": "string (required when status = 'shipped')",
  "note": "string (optional admin note)"
}
```

### Response 200

Updated order object (same as GET detail).

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | INVALID_TRANSITION | Cannot transition from '{current}' to '{target}' |
| 400 | TRACKING_REQUIRED | Tracking number is required when shipping an order |
| 403 | FORBIDDEN | Not an admin user |
| 404 | ORDER_NOT_FOUND | Order does not exist |

---

## POST /api/v1/admin/orders/{order_id}/refund

Initiate a full refund for an order. Updates payment_status to 'refunded'.

### Request Body

```json
{
  "reason": "string (optional, max 500 chars)"
}
```

### Response 200

```json
{
  "order_id": "uuid",
  "order_number": "ORD-20260414-00042",
  "payment_status": "refunded",
  "refund_status": "succeeded",
  "refund_amount": 6048
}
```

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | ALREADY_REFUNDED | This order has already been refunded |
| 400 | REFUND_FAILED | Refund could not be processed |
| 400 | NOT_PAID | Order has not been paid, cannot refund |
| 403 | FORBIDDEN | Not an admin user |
| 404 | ORDER_NOT_FOUND | Order does not exist |

---

## PATCH /api/v1/admin/orders/{order_id}/notes

Update admin notes on an order.

### Request Body

```json
{
  "admin_notes": "string (max 2000 chars)"
}
```

### Response 200

```json
{ "admin_notes": "string" }
```

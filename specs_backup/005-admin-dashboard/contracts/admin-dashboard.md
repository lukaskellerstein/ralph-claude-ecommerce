# API Contract: Admin Dashboard Analytics

All endpoints require authentication with `role = admin`. Returns 403 for non-admin users.

## GET /api/v1/admin/dashboard/stats

Get aggregated dashboard statistics. Results cached for 5 minutes.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| days | integer | No | Time range: 7, 30, or 90. Default: 30 |

### Response 200

```json
{
  "period_days": 30,
  "total_revenue": 1250000,
  "total_orders": 85,
  "average_order_value": 14706,
  "total_customers": 342,
  "daily_revenue": [
    { "date": "2026-03-15", "revenue": 45000 },
    { "date": "2026-03-16", "revenue": 32000 }
  ],
  "top_products": [
    {
      "product_id": "uuid",
      "name": "string",
      "order_count": 25,
      "revenue": 124750
    }
  ],
  "recent_orders": [
    {
      "order_number": "ORD-20260414-00042",
      "customer_name": "string",
      "total": 6048,
      "status": "paid",
      "created_at": "2026-04-14T10:00:00Z"
    }
  ],
  "computed_at": "2026-04-14T10:05:00Z"
}
```

**Note**: All monetary values in cents. `daily_revenue` covers every day in the period (including days with zero revenue). `top_products` lists up to 5 products. `recent_orders` lists up to 5 orders.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | INVALID_PERIOD | Period must be 7, 30, or 90 days |
| 403 | FORBIDDEN | Not an admin user |

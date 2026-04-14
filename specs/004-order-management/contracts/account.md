# API Contract: Account Dashboard

## GET /api/v1/account/dashboard

Get aggregated summary data for the account dashboard. Requires authentication.

### Response 200

```json
{
  "recent_order": {
    "order_number": "ORD-20260414-00042",
    "status": "paid",
    "total": 6048,
    "created_at": "2026-04-14T10:00:00Z"
  },
  "address_count": 2,
  "wishlist_count": 5,
  "profile_complete": true
}
```

**Note**: `recent_order` is null if the user has no orders. `profile_complete` is true when the user has first_name, last_name, and phone filled in.

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 401 | NOT_AUTHENTICATED | Not authenticated |

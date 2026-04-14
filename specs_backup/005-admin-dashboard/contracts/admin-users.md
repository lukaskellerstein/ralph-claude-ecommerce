# API Contract: Admin Users

All endpoints require authentication with `role = admin`. Returns 403 for non-admin users.

## GET /api/v1/admin/users

List all registered users with search and pagination.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | No | Search by email or name |
| role | string | No | Filter by role: 'customer' or 'admin' |
| is_active | boolean | No | Filter by active status |
| after | string | No | Cursor for pagination |
| page_size | integer | No | Items per page (1-100). Default: 25 |

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "role": "customer",
      "is_active": true,
      "order_count": 5,
      "created_at": "2026-04-14T10:00:00Z"
    }
  ],
  "next_cursor": "string | null",
  "has_next_page": true,
  "total_count": 250
}
```

---

## PATCH /api/v1/admin/users/{user_id}

Update a user's role or active status. Cannot edit name, email, or password.

### Request Body (at least one required)

```json
{
  "role": "admin",
  "is_active": true
}
```

### Response 200

Updated user object (same fields as list item).

### Error Responses

| Status | Code | Detail |
|--------|------|--------|
| 400 | LAST_ADMIN | Cannot demote or deactivate the last admin user |
| 403 | FORBIDDEN | Not an admin user |
| 404 | USER_NOT_FOUND | User does not exist |
| 422 | VALIDATION_ERROR | Invalid role value |

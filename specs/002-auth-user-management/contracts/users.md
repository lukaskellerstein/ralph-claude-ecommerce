# API Contract: Users

## GET /api/v1/users/me

Get the authenticated user's profile. Requires authentication.

### Response 200

```json
{
  "id": "uuid",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "phone": "string | null",
  "role": "string",
  "created_at": "ISO 8601 timestamp"
}
```

### Response 401

```json
{
  "detail": "Not authenticated",
  "code": "NOT_AUTHENTICATED"
}
```

---

## PATCH /api/v1/users/me

Update the authenticated user's profile. Requires authentication. Only provided fields are updated.

### Request Body

All fields optional — only include fields to update.

```json
{
  "first_name": "string (1-100 chars, optional)",
  "last_name": "string (1-100 chars, optional)",
  "phone": "string (valid phone format, optional, send null to clear)"
}
```

### Response 200

```json
{
  "id": "uuid",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "phone": "string | null",
  "role": "string",
  "created_at": "ISO 8601 timestamp"
}
```

### Response 401

```json
{
  "detail": "Not authenticated",
  "code": "NOT_AUTHENTICATED"
}
```

### Response 422

```json
{
  "detail": "Validation error description",
  "code": "VALIDATION_ERROR"
}
```

---

## GET /api/v1/users/me/addresses

List the authenticated user's saved addresses. Requires authentication.

### Response 200

```json
{
  "items": [
    {
      "id": "uuid",
      "label": "string",
      "street_line_1": "string",
      "street_line_2": "string | null",
      "city": "string",
      "state": "string",
      "postal_code": "string",
      "country": "string",
      "is_default": true
    }
  ]
}
```

### Response 401

```json
{
  "detail": "Not authenticated",
  "code": "NOT_AUTHENTICATED"
}
```

---

## POST /api/v1/users/me/addresses

Add a new address. Requires authentication. Maximum 5 addresses per user.

### Request Body

```json
{
  "label": "string (1-50 chars, required)",
  "street_line_1": "string (1-255 chars, required)",
  "street_line_2": "string (1-255 chars, optional)",
  "city": "string (1-100 chars, required)",
  "state": "string (1-100 chars, required)",
  "postal_code": "string (1-20 chars, required)",
  "country": "string (1-100 chars, required)",
  "is_default": "boolean (optional, default false)"
}
```

### Response 201

```json
{
  "id": "uuid",
  "label": "string",
  "street_line_1": "string",
  "street_line_2": "string | null",
  "city": "string",
  "state": "string",
  "postal_code": "string",
  "country": "string",
  "is_default": false
}
```

### Response 400

```json
{
  "detail": "Maximum of 5 addresses reached",
  "code": "ADDRESS_LIMIT_REACHED"
}
```

### Response 401

```json
{
  "detail": "Not authenticated",
  "code": "NOT_AUTHENTICATED"
}
```

### Response 422

```json
{
  "detail": "Validation error description",
  "code": "VALIDATION_ERROR"
}
```

---

## PATCH /api/v1/users/me/addresses/:id

Update an existing address. Requires authentication. User can only update their own addresses.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Address ID |

### Request Body

All fields optional — only include fields to update.

```json
{
  "label": "string (1-50 chars, optional)",
  "street_line_1": "string (1-255 chars, optional)",
  "street_line_2": "string (1-255 chars, optional, send null to clear)",
  "city": "string (1-100 chars, optional)",
  "state": "string (1-100 chars, optional)",
  "postal_code": "string (1-20 chars, optional)",
  "country": "string (1-100 chars, optional)",
  "is_default": "boolean (optional)"
}
```

### Response 200

```json
{
  "id": "uuid",
  "label": "string",
  "street_line_1": "string",
  "street_line_2": "string | null",
  "city": "string",
  "state": "string",
  "postal_code": "string",
  "country": "string",
  "is_default": true
}
```

### Response 401

```json
{
  "detail": "Not authenticated",
  "code": "NOT_AUTHENTICATED"
}
```

### Response 404

```json
{
  "detail": "Address not found",
  "code": "NOT_FOUND"
}
```

---

## DELETE /api/v1/users/me/addresses/:id

Delete an address. Requires authentication. User can only delete their own addresses. If the deleted address was the default, the oldest remaining address is promoted to default.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Address ID |

### Response 204

No content.

### Response 401

```json
{
  "detail": "Not authenticated",
  "code": "NOT_AUTHENTICATED"
}
```

### Response 404

```json
{
  "detail": "Address not found",
  "code": "NOT_FOUND"
}
```

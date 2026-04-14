# API Contract: Authentication

## POST /api/v1/auth/register

Register a new user account.

### Request Body

```json
{
  "email": "string (valid email, required)",
  "password": "string (min 8 chars, at least 1 letter + 1 number, required)",
  "first_name": "string (1-100 chars, required)",
  "last_name": "string (1-100 chars, required)"
}
```

### Response 201

Sets `access_token` and `refresh_token` httpOnly cookies.

```json
{
  "id": "uuid",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "customer"
}
```

### Response 409

```json
{
  "detail": "An account with this email already exists",
  "code": "EMAIL_ALREADY_EXISTS"
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

## POST /api/v1/auth/login

Authenticate an existing user.

### Request Body

```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

### Response 200

Sets `access_token` and `refresh_token` httpOnly cookies.

```json
{
  "id": "uuid",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "string"
}
```

### Response 401

```json
{
  "detail": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
}
```

### Response 423

```json
{
  "detail": "Account temporarily locked. Try again later.",
  "code": "ACCOUNT_LOCKED"
}
```

### Response 429

```json
{
  "detail": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

---

## POST /api/v1/auth/logout

End the current session. Requires authentication.

### Request

No body. Reads `refresh_token` from cookie.

### Response 200

Clears `access_token` and `refresh_token` cookies.

```json
{
  "detail": "Logged out successfully"
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

## POST /api/v1/auth/refresh

Obtain a new access token using a valid refresh token.

### Request

No body. Reads `refresh_token` from cookie.

### Response 200

Sets new `access_token` cookie.

```json
{
  "detail": "Token refreshed"
}
```

### Response 401

```json
{
  "detail": "Invalid or expired refresh token",
  "code": "INVALID_REFRESH_TOKEN"
}
```

---

## POST /api/v1/auth/forgot-password

Request a password reset link. Always returns success regardless of whether the email exists (prevents email enumeration).

### Request Body

```json
{
  "email": "string (required)"
}
```

### Response 200

```json
{
  "detail": "If an account exists, a reset link has been sent"
}
```

### Response 429

```json
{
  "detail": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

---

## POST /api/v1/auth/reset-password

Set a new password using a valid reset token.

### Request Body

```json
{
  "token": "string (the reset token from the URL, required)",
  "new_password": "string (min 8 chars, at least 1 letter + 1 number, required)"
}
```

### Response 200

```json
{
  "detail": "Password reset successful"
}
```

### Response 400

```json
{
  "detail": "Invalid or expired reset token",
  "code": "INVALID_RESET_TOKEN"
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

## Rate Limiting

All endpoints in `/api/v1/auth/*` are rate-limited to **20 requests per minute per IP**.

Rate limit headers included in all responses:
- `X-RateLimit-Limit`: 20
- `X-RateLimit-Remaining`: remaining requests
- `X-RateLimit-Reset`: seconds until limit resets

## Cookie Specification

| Cookie | httpOnly | Secure | SameSite | Path | Max-Age |
|--------|----------|--------|----------|------|---------|
| access_token | Yes | Yes (prod) | Lax | /api | 900 (15 min) |
| refresh_token | Yes | Yes (prod) | Lax | /api/v1/auth | 604800 (7 days) |

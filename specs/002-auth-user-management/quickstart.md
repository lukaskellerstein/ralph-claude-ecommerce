# Quickstart: Authentication & User Management

**Feature**: Authentication & User Management
**Date**: 2026-04-14

## Prerequisites

- Docker and Docker Compose installed
- The development stack running (`docker compose up`)
- PostgreSQL database available (provided by Docker Compose)

## Development Setup

1. **Start the stack** (if not already running):
   ```bash
   docker compose up
   ```

2. **Run database migrations** to create auth tables:
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Verify the auth endpoints** are available:
   ```bash
   curl http://localhost:8000/docs
   ```
   The OpenAPI docs should list all `/api/v1/auth/*` and `/api/v1/users/*` endpoints.

## Quick Verification

### Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234","first_name":"Jane","last_name":"Doe"}' \
  -c cookies.txt -v
```

Expected: 201 response with user data. `Set-Cookie` headers for `access_token` and `refresh_token`.

### Log in

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}' \
  -c cookies.txt -v
```

Expected: 200 response with user data. Cookies set.

### Get profile

```bash
curl http://localhost:8000/api/v1/users/me \
  -b cookies.txt
```

Expected: 200 response with user profile.

### Log out

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -b cookies.txt -c cookies.txt -v
```

Expected: 200 response. Cookies cleared.

## Running Tests

```bash
cd backend
pytest tests/test_auth.py tests/test_users.py -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| JWT_SECRET_KEY | Secret key for signing JWT access tokens | (required) |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime | 15 |
| JWT_REFRESH_TOKEN_EXPIRE_DAYS | Refresh token lifetime | 7 |
| SMTP_HOST | SMTP server host (production only) | (empty = console logging) |
| SMTP_PORT | SMTP server port | 587 |
| SMTP_USER | SMTP username | (empty) |
| SMTP_PASSWORD | SMTP password | (empty) |
| PASSWORD_RESET_URL_BASE | Base URL for reset links | http://localhost:5173/reset-password |
| CORS_ORIGINS | Comma-separated allowed origins | http://localhost:5173 |

## Key Files

### Backend

| File | Purpose |
|------|---------|
| `backend/app/api/v1/auth.py` | Auth endpoints (register, login, logout, refresh, forgot/reset password) |
| `backend/app/api/v1/users.py` | User profile and address endpoints |
| `backend/app/models/user.py` | User, Address SQLAlchemy models |
| `backend/app/models/token.py` | RefreshToken, PasswordResetToken models |
| `backend/app/schemas/auth.py` | Auth request/response Pydantic schemas |
| `backend/app/schemas/user.py` | User/address Pydantic schemas |
| `backend/app/services/auth_service.py` | Auth business logic (password hashing, token generation, lockout) |
| `backend/app/services/user_service.py` | Profile and address business logic |
| `backend/app/services/email_service.py` | Email sender interface + console/SMTP implementations |
| `backend/app/core/security.py` | JWT encoding/decoding, password hashing utilities |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/pages/login.tsx` | Login page |
| `frontend/src/pages/register.tsx` | Registration page |
| `frontend/src/pages/forgot-password.tsx` | Forgot password page |
| `frontend/src/pages/reset-password.tsx` | Reset password form (with token from URL) |
| `frontend/src/pages/profile.tsx` | User profile page |
| `frontend/src/pages/addresses.tsx` | Saved addresses management page |
| `frontend/src/hooks/use-auth.ts` | Auth state hook (current user, isAuthenticated) |
| `frontend/src/components/protected-route.tsx` | Route guard for authenticated pages |
| `frontend/src/components/user-menu.tsx` | Header user menu (login/register or profile/logout) |

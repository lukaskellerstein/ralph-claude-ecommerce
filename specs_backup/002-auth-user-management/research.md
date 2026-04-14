# Research: Authentication & User Management

**Feature**: Authentication & User Management
**Date**: 2026-04-14

## R-001: JWT Token Strategy (Access + Refresh)

**Decision**: Dual-token strategy with short-lived access tokens (15 min) and long-lived refresh tokens (7 days), both transported via httpOnly secure cookies.

**Rationale**: httpOnly cookies prevent XSS-based token theft (JavaScript cannot read the cookie). Short-lived access tokens limit the damage window if a token is compromised. Refresh tokens enable seamless session continuity without re-login. This aligns with Constitution Principle V (Security) and the spec's FR-002.

**Alternatives considered**:
- **localStorage tokens**: Rejected — vulnerable to XSS attacks; JavaScript can read and exfiltrate tokens.
- **Session-based auth (server-side sessions)**: Rejected — requires server-side session store, complicates horizontal scaling, and contradicts the JWT decision in the Constitution (Principle II).
- **Single long-lived token**: Rejected — larger compromise window; no way to force re-authentication.

**Implementation notes**:
- Access token: JWT with `sub` (user UUID), `role`, `exp` (15 min). Signed with HS256 using a secret from `.env`.
- Refresh token: Opaque random token stored in the database (not a JWT). Enables server-side revocation.
- Both cookies: `httpOnly`, `Secure` (HTTPS only in production), `SameSite=Lax`, `Path=/api`.
- Access token cookie name: `access_token`. Refresh token cookie name: `refresh_token`.

---

## R-002: Password Hashing with bcrypt

**Decision**: Use bcrypt with a work factor of 12 for password hashing.

**Rationale**: Constitution Principle V mandates bcrypt. Work factor 12 provides a good balance between security (~250ms hash time) and user experience. The `passlib` library with bcrypt backend is the standard Python choice.

**Alternatives considered**:
- **Argon2**: Superior algorithm (memory-hard), but Constitution explicitly mandates bcrypt. Could be considered in a future amendment.
- **scrypt**: Similar to Argon2 in being memory-hard, but again overridden by Constitution mandate.
- **Lower work factor (10)**: Rejected — too fast for modern hardware to resist brute-force.

**Implementation notes**:
- Library: `passlib[bcrypt]` with `CryptContext(schemes=["bcrypt"], deprecated="auto")`.
- Password is never logged or returned in any API response (FR-001).

---

## R-003: Account Lockout Strategy

**Decision**: Track failed login attempts per user in the database. After 5 failures within a 15-minute sliding window, lock the account for 30 minutes.

**Rationale**: This directly implements FR-004. Database-backed tracking ensures lockout state survives server restarts. The sliding window prevents accumulation over long periods from triggering lockout.

**Alternatives considered**:
- **IP-based lockout only**: Rejected — attackers can use multiple IPs; doesn't protect specific accounts.
- **CAPTCHA after N failures**: Useful addition but spec requires lockout, not CAPTCHA. Can be layered on later.
- **Redis-backed lockout**: Could be faster but adds an infrastructure dependency. For v1, PostgreSQL is sufficient given the low frequency of lockout checks.

**Implementation notes**:
- Fields on User model: `failed_login_count` (INTEGER), `last_failed_login_at` (TIMESTAMP), `locked_until` (TIMESTAMP NULLABLE).
- On each failed login: if `last_failed_login_at` is older than 15 minutes, reset `failed_login_count` to 1; otherwise increment.
- When `failed_login_count` reaches 5: set `locked_until = now() + 30 minutes`.
- On login check: if `locked_until > now()`, reject with "Account temporarily locked" message.
- On successful login: reset `failed_login_count` to 0 and clear `locked_until`.

---

## R-004: Rate Limiting Strategy

**Decision**: Use `slowapi` (built on `limits` library) for per-IP rate limiting on auth endpoints at 20 requests/minute.

**Rationale**: FR-009 requires 20 req/min/IP on auth endpoints. `slowapi` integrates natively with FastAPI, supports in-memory storage for development and Redis for production. It uses standard rate limit headers (`X-RateLimit-*`, `Retry-After`).

**Alternatives considered**:
- **Nginx-level rate limiting**: Good for production but doesn't help during development. Can be layered on top.
- **Custom middleware**: Unnecessary complexity when `slowapi` exists.
- **Redis-backed from day 1**: Overkill for v1; in-memory storage is fine for single-instance development.

**Implementation notes**:
- Apply `@limiter.limit("20/minute")` to all routes in `api/v1/auth.py`.
- Return `429 Too Many Requests` with `Retry-After` header.
- Error response follows Constitution format: `{ "detail": "Rate limit exceeded", "code": "RATE_LIMIT_EXCEEDED" }`.

---

## R-005: Password Reset Token Generation

**Decision**: Use `secrets.token_urlsafe(32)` for generating cryptographically random password reset tokens, stored hashed (SHA-256) in the database.

**Rationale**: FR-010 requires cryptographically random, single-use, 1-hour expiry tokens. Storing the token hashed prevents a database breach from exposing valid reset tokens. `secrets.token_urlsafe` uses the OS CSPRNG.

**Alternatives considered**:
- **UUID v4 as token**: Rejected — UUIDs are not guaranteed to be cryptographically random in all implementations.
- **Storing token in plaintext**: Rejected — if the database is compromised, all pending reset tokens would be exposed.
- **JWT-based reset token**: Rejected — cannot be revoked server-side (unless maintaining a blocklist, which defeats the purpose).

**Implementation notes**:
- Generate: `token = secrets.token_urlsafe(32)` → send this in the reset URL.
- Store: `hashed_token = hashlib.sha256(token.encode()).hexdigest()` in `password_reset_tokens` table.
- Verify: hash the incoming token and compare against stored hash.
- Fields: `hashed_token`, `user_id`, `expires_at`, `used_at` (NULLABLE).

---

## R-006: Email Delivery for Password Reset

**Decision**: Use a pluggable email interface. Development: log the reset URL to console/stdout. Production: configure SMTP via environment variables.

**Rationale**: The spec assumes console logging in development. A simple abstraction (interface/protocol) allows swapping the backend without changing business logic.

**Alternatives considered**:
- **Always require SMTP**: Rejected — unnecessary complexity for local development.
- **Use a transactional email service SDK (SendGrid, SES)**: Good for production but overkill for v1. The pluggable interface allows adding this later.

**Implementation notes**:
- Define an `EmailSender` protocol with `async def send_reset_email(to: str, reset_url: str) -> None`.
- `ConsoleEmailSender`: logs to stdout (default in development).
- `SmtpEmailSender`: uses `aiosmtplib` with config from `.env` (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`).
- Inject via FastAPI dependency.

---

## R-007: CORS Configuration for Auth Cookies

**Decision**: Configure CORS with `allow_credentials=True` and explicit `allow_origins` (no wildcard) to enable cookie-based authentication across frontend/backend.

**Rationale**: httpOnly cookies require `credentials: 'include'` on fetch requests from the frontend. The CORS spec mandates that when `credentials` is true, `Access-Control-Allow-Origin` cannot be `*` — it must list specific origins. Constitution Principle V requires CORS restricted to known frontend origins.

**Implementation notes**:
- `CORS_ORIGINS` env var: comma-separated list (e.g., `http://localhost:5173` for dev).
- FastAPI `CORSMiddleware` with `allow_credentials=True`, `allow_origins=settings.cors_origins`.

---

## R-008: Frontend Auth State Management

**Decision**: Use TanStack Query for auth state. A `useAuth` hook wraps `GET /api/v1/users/me` to determine the current user. Auth state is derived from whether this query succeeds (valid cookie) or fails (401).

**Rationale**: Since tokens are in httpOnly cookies (not accessible to JavaScript), the frontend cannot inspect the token directly. Instead, it makes an API call to determine auth state. TanStack Query handles caching, background refetching, and stale-while-revalidate patterns.

**Alternatives considered**:
- **React Context with localStorage**: Rejected — tokens are httpOnly and not readable by JS.
- **Zustand/Redux for auth state**: Unnecessary — TanStack Query already manages server state. Adding a separate store creates sync issues.

**Implementation notes**:
- `useAuth()` hook: calls `GET /api/v1/users/me`, returns `{ user, isAuthenticated, isLoading }`.
- On 401 response, try `POST /api/v1/auth/refresh` once. If that also fails, redirect to login.
- `ProtectedRoute` component wraps pages requiring auth, redirects to `/login` if not authenticated.

---

## R-009: Address Management Default Promotion Logic

**Decision**: When the default address is deleted, promote the oldest remaining address (by `created_at`) to default. If no addresses remain, no default is set.

**Rationale**: FR-013 requires automatic promotion. Using `created_at` order is predictable and requires no additional user input. The spec says "next address" which we interpret as the oldest remaining.

**Alternatives considered**:
- **Promote most recently created**: Could also work, but "oldest" feels more stable/predictable.
- **Clear default, let user re-pick**: Rejected — spec explicitly says auto-promote.

**Implementation notes**:
- On delete: if deleted address `is_default=true`, query remaining addresses ordered by `created_at ASC`, set first result to `is_default=true`.
- Wrap in a transaction with the delete operation.

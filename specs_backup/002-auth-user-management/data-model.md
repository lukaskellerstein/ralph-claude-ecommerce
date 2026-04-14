# Data Model: Authentication & User Management

**Feature**: Authentication & User Management
**Date**: 2026-04-14

## Entity Relationship Overview

```
User
  ├── Address (one-to-many, max 5, one default)
  ├── RefreshToken (one-to-many, revocable)
  └── PasswordResetToken (one-to-many, single-use)
```

## Entities

### User

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User's email (stored lowercase) |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt-hashed password |
| first_name | VARCHAR(100) | NOT NULL | User's first name |
| last_name | VARCHAR(100) | NOT NULL | User's last name |
| phone | VARCHAR(20) | NULLABLE | Optional phone number |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'customer' | User role: 'customer' or 'admin' |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether account is active |
| failed_login_count | INTEGER | NOT NULL, DEFAULT 0 | Failed login attempts in current window |
| last_failed_login_at | TIMESTAMP | NULLABLE | Timestamp of most recent failed login |
| locked_until | TIMESTAMP | NULLABLE | Account locked until this time (NULL = not locked) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `email` (unique, case-insensitive via `LOWER(email)`), `role`
**Constraints**: `email` stored as lowercase on insert/update. `role` CHECK constraint: `role IN ('customer', 'admin')`.

---

### Address

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User(id), NOT NULL, ON DELETE CASCADE | Owning user |
| label | VARCHAR(50) | NOT NULL | Display label (e.g., "Home", "Work") |
| street_line_1 | VARCHAR(255) | NOT NULL | Primary street address |
| street_line_2 | VARCHAR(255) | NULLABLE | Secondary street address (apt, suite, etc.) |
| city | VARCHAR(100) | NOT NULL | City |
| state | VARCHAR(100) | NOT NULL | State or province |
| postal_code | VARCHAR(20) | NOT NULL | Postal/ZIP code |
| country | VARCHAR(100) | NOT NULL | Country |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether this is the user's default address |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `user_id`, `(user_id, is_default)`
**Constraints**: Maximum 5 addresses per user (enforced at application level). At most one address per user can have `is_default=true` (enforced at application level within transaction).
**Delete behavior**: Hard delete (addresses are ephemeral data per Constitution Principle VII).

---

### RefreshToken

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User(id), NOT NULL, ON DELETE CASCADE | Token owner |
| token_hash | VARCHAR(64) | NOT NULL, UNIQUE | SHA-256 hash of the opaque refresh token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time (7 days from creation) |
| revoked_at | TIMESTAMP | NULLABLE | When the token was revoked (NULL = active) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**: `token_hash` (unique), `user_id`, `expires_at`
**Delete behavior**: Hard delete (session data is ephemeral per Constitution Principle VII). Expired/revoked tokens can be cleaned up by a periodic job.

---

### PasswordResetToken

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User(id), NOT NULL, ON DELETE CASCADE | User requesting the reset |
| token_hash | VARCHAR(64) | NOT NULL, UNIQUE | SHA-256 hash of the reset token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time (1 hour from creation) |
| used_at | TIMESTAMP | NULLABLE | When the token was used (NULL = unused) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**: `token_hash` (unique), `user_id`, `expires_at`
**Delete behavior**: Hard delete (ephemeral data). Old tokens can be cleaned up periodically.
**Constraints**: When a new reset token is created for a user, all previous unused tokens for that user are invalidated (set `used_at = NOW()`).

---

## State Transitions

### User Account States

```
Active (is_active=true, locked_until=NULL or past)
  → Locked (locked_until > now())              [5 failed logins in 15 min]
  → Deactivated (is_active=false)               [admin action]

Locked → Active                                  [lockout period expires, or successful password reset]
Deactivated → Active                             [admin re-enables account]
```

- Active users can log in, access protected pages, and manage their profile/addresses.
- Locked users cannot log in but can still request password resets (lockout only affects login).
- Deactivated users cannot log in or access any protected resources.

### Refresh Token Lifecycle

```
Active (revoked_at=NULL, expires_at > now())
  → Revoked (revoked_at=timestamp)              [logout or password change]
  → Expired (expires_at <= now())               [natural expiry after 7 days]
```

### Password Reset Token Lifecycle

```
Pending (used_at=NULL, expires_at > now())
  → Used (used_at=timestamp)                    [user sets new password]
  → Expired (expires_at <= now())               [natural expiry after 1 hour]
  → Invalidated (used_at=NOW())                 [new reset token requested]
```

## Validation Rules

| Entity | Rule |
|--------|------|
| User | `email` must be a valid email format, stored lowercase, unique |
| User | Password must be at least 8 characters with at least one letter and one number (validated pre-hash) |
| User | `first_name` must be 1-100 characters |
| User | `last_name` must be 1-100 characters |
| User | `phone` if provided must be a valid phone format (digits, spaces, dashes, plus sign, max 20 chars) |
| User | `role` must be one of: 'customer', 'admin' |
| Address | `label` must be 1-50 characters |
| Address | `street_line_1` must be 1-255 characters |
| Address | `city` must be 1-100 characters |
| Address | `state` must be 1-100 characters |
| Address | `postal_code` must be 1-20 characters |
| Address | `country` must be 1-100 characters |
| Address | Maximum 5 addresses per user |
| Address | At most one default address per user |
| RefreshToken | `token_hash` must be a valid SHA-256 hex digest (64 chars) |
| PasswordResetToken | `token_hash` must be a valid SHA-256 hex digest (64 chars) |

## Cross-Feature References

- **Review** (from 001-product-catalog) has `user_id` FK → `User(id)`. The User entity defined here is the referenced table.
- Future features (orders, cart) will also reference `User(id)` and potentially `Address(id)`.

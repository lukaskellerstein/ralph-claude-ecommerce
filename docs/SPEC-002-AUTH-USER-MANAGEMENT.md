# Feature Specification: Authentication & User Management

| Field          | Value                          |
|----------------|--------------------------------|
| Feature Branch | 002-auth-and-users             |
| Created        | 2026-04-14                     |
| Status         | Draft                          |

## 1. Overview

Authentication and user management provides the foundation for all personalized features: shopping carts, order history, reviews, and account settings. The system supports email/password registration, secure JWT-based sessions, and user profile management.

## 2. User Stories

### US-001: Register a New Account

**As a** visitor,
**I want to** create an account with my email and password,
**So that** I can place orders and track my purchase history.

**Acceptance Criteria:**

- Registration form collects: email, password, first name, last name.
- Email must be unique — duplicate email shows a clear error message.
- Password must be at least 8 characters with at least one letter and one number.
- Password strength indicator is displayed in real-time.
- After successful registration, user is automatically logged in and redirected to the homepage.
- A welcome confirmation is displayed (toast notification).
- Registration is available via `POST /api/v1/auth/register`.

**Independent Test:** Can be fully tested by filling out the registration form with valid data, submitting, and verifying the user is logged in and can access protected pages.

### US-002: Log In to an Existing Account

**As a** registered user,
**I want to** log in with my email and password,
**So that** I can access my account, cart, and order history.

**Acceptance Criteria:**

- Login form collects: email and password.
- Successful login sets an httpOnly JWT cookie and redirects to the previous page (or homepage).
- Invalid credentials show a generic error: "Invalid email or password" (no indication of which field is wrong).
- After 5 failed attempts within 15 minutes, the account is temporarily locked for 30 minutes.
- Login is available via `POST /api/v1/auth/login`.

**Independent Test:** Can be fully tested by logging in with known valid credentials and verifying access to a protected endpoint, then using invalid credentials and verifying the error response.

### US-003: Log Out

**As a** logged-in user,
**I want to** log out of my account,
**So that** my session is ended and my account is secured on shared devices.

**Acceptance Criteria:**

- A "Log out" action is accessible from the user menu in the header.
- Logging out clears the JWT cookie and redirects to the homepage.
- After logout, accessing protected pages redirects to the login page.
- Logout is available via `POST /api/v1/auth/logout`.

**Independent Test:** Can be fully tested by logging in, clicking logout, and verifying protected pages are no longer accessible.

### US-004: Reset Forgotten Password

**As a** registered user who forgot their password,
**I want to** reset my password via email,
**So that** I can regain access to my account.

**Acceptance Criteria:**

- A "Forgot password?" link is on the login page.
- User enters their email on the password reset request page.
- System always shows "If an account exists, a reset link has been sent" (no email enumeration).
- Reset token is valid for 1 hour and single-use.
- Reset link leads to a form where the user sets a new password.
- After successful reset, user is redirected to the login page with a success message.
- Endpoints: `POST /api/v1/auth/forgot-password`, `POST /api/v1/auth/reset-password`.

**Independent Test:** Can be fully tested by requesting a reset for a known email, using the token to set a new password, and verifying login works with the new password.

[NEEDS CLARIFICATION: Email delivery mechanism for v1 — use a real SMTP service, or log reset links to console for development?]

### US-005: View and Edit Profile

**As a** logged-in user,
**I want to** view and update my profile information,
**So that** my account details stay current.

**Acceptance Criteria:**

- Profile page shows: email (read-only), first name, last name, phone number (optional).
- User can update first name, last name, and phone number.
- Changes are saved via `PATCH /api/v1/users/me`.
- A success toast confirms the update.
- Email change is out of scope for v1.

**Independent Test:** Can be fully tested by navigating to the profile page, changing the last name, saving, and refreshing to verify the change persisted.

### US-006: Manage Saved Addresses

**As a** logged-in user,
**I want to** save, edit, and delete shipping addresses,
**So that** I can quickly select an address during checkout.

**Acceptance Criteria:**

- Address form collects: label (e.g., "Home"), street line 1, street line 2 (optional), city, state/province, postal code, country.
- User can have up to 5 saved addresses.
- One address can be marked as "default."
- Addresses are managed via CRUD endpoints: `GET/POST /api/v1/users/me/addresses`, `PATCH/DELETE /api/v1/users/me/addresses/:id`.
- Deleting the default address auto-promotes the next address (if any) to default.

**Independent Test:** Can be fully tested by creating an address, editing it, marking another as default, deleting the first, and verifying the state after each operation.

## 3. Functional Requirements

- **FR-001:** System MUST hash passwords using bcrypt before storage.
- **FR-002:** System MUST issue JWT access tokens (15 min expiry) and refresh tokens (7 day expiry) stored in httpOnly cookies.
- **FR-003:** System MUST provide a `POST /api/v1/auth/refresh` endpoint to issue new access tokens using a valid refresh token.
- **FR-004:** System MUST enforce account lockout after 5 failed login attempts within 15 minutes, locking the account for 30 minutes.
- **FR-005:** System MUST validate email format and password complexity on registration.
- **FR-006:** System MUST NOT reveal whether an email exists in the system during login failure or password reset.
- **FR-007:** System MUST provide a `GET /api/v1/users/me` endpoint returning the authenticated user's profile.
- **FR-008:** System MUST support role-based access: `customer` (default) and `admin`.
- **FR-009:** System MUST rate-limit auth endpoints to 20 requests per minute per IP.
- **FR-010:** Password reset tokens MUST be cryptographically random, single-use, and expire after 1 hour.

## 4. Core Entities (What, Not How)

- **User:** A registered person. Key attributes: email, hashed password, first name, last name, phone, role (customer/admin), active status, lockout state.
- **Address:** A shipping/billing address belonging to a user. Key attributes: label, street lines, city, state, postal code, country, is_default flag.
- **Session/RefreshToken:** Tracks active refresh tokens per user. Allows revocation on logout or password change.

## 5. Success Criteria

- **SC-001:** Users can register and log in within 30 seconds on first attempt.
- **SC-002:** Auth endpoints respond in under 300ms p95.
- **SC-003:** No plaintext passwords exist anywhere in the system (database, logs, API responses).
- **SC-004:** Account lockout successfully blocks brute-force attempts.

## 6. Assumptions and Dependencies

- Email delivery for password resets uses console logging in development; pluggable SMTP for production.
- OAuth/social login (Google, GitHub) is out of scope for v1.
- Two-factor authentication is out of scope for v1.
- User avatars/profile pictures are out of scope for v1.

## 7. Out of Scope

- Social/OAuth login providers.
- Two-factor authentication (2FA).
- Email verification on registration (v1 trusts the provided email).
- Account deletion / GDPR data export (deferred to a future spec).
- Admin user management (handled in spec 005).

## 8. Review & Acceptance Checklist

- [ ] All user stories have clear acceptance criteria
- [ ] Functional requirements are testable and unambiguous
- [ ] No implementation details leaked into the spec (tech-agnostic "what")
- [ ] All ambiguities marked with [NEEDS CLARIFICATION]
- [ ] Success criteria are measurable
- [ ] Out of scope items are explicitly listed
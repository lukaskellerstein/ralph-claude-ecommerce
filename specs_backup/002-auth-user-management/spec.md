# Feature Specification: Authentication & User Management

**Feature Branch**: `002-auth-user-management`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: User description: "Authentication and user management - email/password registration, JWT sessions, profile management, saved addresses"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register a New Account (Priority: P1)

A visitor wants to create an account with their email and password so they can place orders and track their purchase history. The registration process collects their email, password, first name, and last name, validates the inputs, and upon success automatically logs them in and redirects them to the homepage with a welcome confirmation.

**Why this priority**: Account creation is the gateway to all personalized features. Without registration, no user can access carts, orders, reviews, or profile settings. This is the foundational user journey.

**Independent Test**: Can be fully tested by filling out the registration form with valid data, submitting, and verifying the user is logged in and can access protected pages. Delivers immediate value as a standalone feature.

**Acceptance Scenarios**:

1. **Given** a visitor on the registration page, **When** they submit valid email, password, first name, and last name, **Then** an account is created, they are automatically logged in, redirected to the homepage, and a welcome toast notification is displayed.
2. **Given** a visitor on the registration page, **When** they submit an email that is already registered, **Then** a clear error message is displayed indicating the email is already in use.
3. **Given** a visitor on the registration page, **When** they enter a password shorter than 8 characters or missing a letter or number, **Then** the form shows a validation error and a real-time password strength indicator guides them.
4. **Given** a visitor on the registration page, **When** they submit an invalid email format, **Then** the form shows an email validation error before submission.

---

### User Story 2 - Log In and Log Out (Priority: P1)

A registered user wants to log in with their email and password to access their account, cart, and order history. They also want to log out to secure their account on shared devices. Login sets a secure session, and logout clears it entirely.

**Why this priority**: Login/logout is equally foundational to registration — users cannot interact with any personalized feature without being authenticated. This is a core P1 alongside registration.

**Independent Test**: Can be fully tested by logging in with known valid credentials and verifying access to a protected page, then logging out and verifying protected pages redirect to the login page.

**Acceptance Scenarios**:

1. **Given** a registered user on the login page, **When** they submit valid email and password, **Then** they are logged in and redirected to their previous page (or homepage).
2. **Given** a user on the login page, **When** they submit invalid credentials, **Then** a generic error message "Invalid email or password" is displayed (no indication of which field is wrong).
3. **Given** a user who has failed login 5 times within 15 minutes, **When** they attempt another login, **Then** the account is temporarily locked for 30 minutes and an appropriate message is displayed.
4. **Given** a logged-in user, **When** they click "Log out" from the user menu in the header, **Then** their session is ended, they are redirected to the homepage, and accessing protected pages redirects to the login page.

---

### User Story 3 - Reset Forgotten Password (Priority: P2)

A registered user who has forgotten their password wants to reset it via email so they can regain access to their account. They request a reset link from the login page, receive it by email, and set a new password through a secure form.

**Why this priority**: Password reset is critical for user retention — without it, users who forget their password are permanently locked out. It is a P2 because it depends on the login flow existing first.

**Independent Test**: Can be fully tested by requesting a reset for a known email, using the token to set a new password, and verifying login works with the new password.

**Acceptance Scenarios**:

1. **Given** a user on the login page, **When** they click "Forgot password?" and submit their email, **Then** the system always shows "If an account exists, a reset link has been sent" regardless of whether the email exists.
2. **Given** a user who has received a password reset link, **When** they click the link within 1 hour, **Then** they are taken to a form where they can set a new password.
3. **Given** a user who has received a password reset link, **When** they click the link after 1 hour has passed, **Then** the link is expired and they are informed to request a new one.
4. **Given** a user who has already used a reset link, **When** they try to use the same link again, **Then** the link is invalid (single-use) and they are informed to request a new one.
5. **Given** a user who has successfully set a new password, **When** they are redirected to the login page, **Then** a success message is displayed and they can log in with their new password.

---

### User Story 4 - View and Edit Profile (Priority: P2)

A logged-in user wants to view and update their profile information so their account details stay current. They can see their email (read-only), and edit their first name, last name, and phone number.

**Why this priority**: Profile management enhances the user experience and is needed before checkout (shipping details). It is P2 because it builds on the authenticated session from P1 stories.

**Independent Test**: Can be fully tested by navigating to the profile page, changing the last name, saving, and refreshing to verify the change persisted.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the profile page, **When** the page loads, **Then** their email (read-only), first name, last name, and phone number (optional) are displayed.
2. **Given** a logged-in user on the profile page, **When** they update their first name, last name, or phone number and save, **Then** a success toast confirms the update and the changes persist on page refresh.
3. **Given** a non-authenticated visitor, **When** they try to access the profile page, **Then** they are redirected to the login page.

---

### User Story 5 - Manage Saved Addresses (Priority: P3)

A logged-in user wants to save, edit, and delete shipping addresses so they can quickly select an address during checkout. They can have up to 5 saved addresses and mark one as the default.

**Why this priority**: Address management is a convenience feature that improves checkout speed. It is P3 because it requires auth and profile to be in place, and checkout can function with manual address entry.

**Independent Test**: Can be fully tested by creating an address, editing it, marking another as default, deleting the first, and verifying the state after each operation.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the addresses page, **When** they add a new address with label, street, city, state/province, postal code, and country, **Then** the address is saved and displayed in their address list.
2. **Given** a logged-in user with 5 saved addresses, **When** they attempt to add another address, **Then** they are informed they have reached the maximum limit of 5 addresses.
3. **Given** a logged-in user with multiple addresses, **When** they mark an address as "default," **Then** that address becomes the default and any previous default is unset.
4. **Given** a logged-in user, **When** they delete the default address and other addresses exist, **Then** the next address is automatically promoted to default.
5. **Given** a logged-in user, **When** they edit an existing address and save, **Then** the changes persist and the updated address is displayed.

---

### Edge Cases

- What happens when a user registers with an email that differs only in letter casing (e.g., "User@Example.com" vs "user@example.com")? Email comparison must be case-insensitive.
- What happens when a user's session expires mid-action (e.g., while editing their profile)? The user should be redirected to login with their changes preserved if possible.
- What happens when a user attempts to reset their password while their account is locked? The reset flow should still work — lockout only blocks login attempts.
- What happens when multiple password reset requests are made? Only the most recent reset token should be valid; previous tokens are invalidated.
- What happens when a user submits the registration form multiple times rapidly? The system should prevent duplicate account creation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST hash passwords before storage using a secure one-way hashing algorithm. Plaintext passwords must never be stored, logged, or returned in any response.
- **FR-002**: System MUST issue short-lived access tokens (15-minute expiry) and longer-lived refresh tokens (7-day expiry) stored in secure, httpOnly cookies.
- **FR-003**: System MUST provide a token refresh mechanism to issue new access tokens using a valid refresh token, enabling seamless session continuity.
- **FR-004**: System MUST enforce account lockout after 5 failed login attempts within 15 minutes, locking the account for 30 minutes.
- **FR-005**: System MUST validate email format and password complexity (minimum 8 characters, at least one letter and one number) on registration.
- **FR-006**: System MUST NOT reveal whether an email exists in the system during login failure or password reset (no email enumeration).
- **FR-007**: System MUST provide authenticated users access to their own profile information.
- **FR-008**: System MUST support role-based access with at least two roles: customer (default on registration) and admin.
- **FR-009**: System MUST rate-limit authentication-related actions to prevent abuse (20 requests per minute per IP).
- **FR-010**: Password reset tokens MUST be cryptographically random, single-use, and expire after 1 hour.
- **FR-011**: System MUST treat email addresses as case-insensitive for uniqueness checks and login.
- **FR-012**: System MUST limit each user to a maximum of 5 saved addresses.
- **FR-013**: System MUST automatically promote the next available address to default when the current default address is deleted.
- **FR-014**: System MUST invalidate all active refresh tokens when a user changes their password.
- **FR-015**: System MUST display a real-time password strength indicator during registration.

### Key Entities

- **User**: A registered person. Key attributes: email, hashed password, first name, last name, phone (optional), role (customer/admin), active status, lockout state (failed attempt count, lockout expiry).
- **Address**: A shipping/billing address belonging to a user. Key attributes: label, street line 1, street line 2 (optional), city, state/province, postal code, country, is_default flag. A user may have up to 5 addresses.
- **Session/Refresh Token**: Tracks active refresh tokens per user. Enables revocation on logout or password change. Key attributes: token value, user association, expiry, used/revoked status.
- **Password Reset Token**: A single-use, time-limited token for password recovery. Key attributes: token value, user association, expiry, used status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete registration and reach the homepage in under 30 seconds on their first attempt.
- **SC-002**: Users can log in and reach their destination page in under 10 seconds.
- **SC-003**: No plaintext passwords exist anywhere in the system — not in storage, logs, or responses.
- **SC-004**: Account lockout successfully blocks brute-force attempts: after 5 failed logins within 15 minutes, further login attempts are rejected for 30 minutes.
- **SC-005**: Password reset flow can be completed end-to-end (request reset, receive token, set new password, log in) in under 2 minutes.
- **SC-006**: Users can add, edit, and delete addresses with changes reflected immediately and persisting across sessions.
- **SC-007**: 95% of users successfully complete their primary authentication task (register, login, or password reset) on their first attempt without confusion.

## Assumptions

- Email delivery for password resets uses console/log output in development; a pluggable email service will be configured for production.
- OAuth/social login (Google, GitHub, etc.) is out of scope for v1.
- Two-factor authentication (2FA) is out of scope for v1.
- User avatars/profile pictures are out of scope for v1.
- Email change functionality is out of scope for v1 — email is set at registration and displayed as read-only on the profile page.
- Email verification on registration is not required for v1 — the system trusts the provided email address.
- Account deletion and GDPR data export are deferred to a future specification.
- Admin user management (creating/editing admin accounts) is handled in a separate specification.
- Users have access to a modern web browser with cookies enabled.
- The system operates in a single-locale context for v1 (addresses use a universal format with country field).

# Tasks: Authentication & User Management

**Input**: Design documents from `/specs/002-auth-user-management/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add auth-specific dependencies and configuration to the existing project structure established by 001-product-catalog.

- [ ] T001 Add auth dependencies (passlib[bcrypt], python-jose[cryptography], slowapi, aiosmtplib) to backend/pyproject.toml
- [ ] T002 Add auth-related environment variables (JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, PASSWORD_RESET_URL_BASE) to backend/app/core/config.py and .env.example
- [ ] T003 [P] Add zod validation schemas for auth forms (login, register, forgot-password, reset-password, profile, address) in frontend/src/lib/validations.ts
- [ ] T004 [P] Add User and Address TypeScript types to frontend/src/lib/types.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core auth infrastructure that MUST be complete before ANY user story can be implemented.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T005 Create security utilities module with password hashing (bcrypt via passlib) and JWT encode/decode functions in backend/app/core/security.py
- [ ] T006 Create User and Address SQLAlchemy models in backend/app/models/user.py per data-model.md (UUID PK, email unique lowercase, hashed_password, first_name, last_name, phone, role, is_active, lockout fields, created_at, updated_at for User; all address fields with is_default for Address)
- [ ] T007 [P] Create RefreshToken and PasswordResetToken SQLAlchemy models in backend/app/models/token.py per data-model.md (token_hash SHA-256, expires_at, revoked_at/used_at)
- [ ] T008 Create Alembic migration for users, addresses, refresh_tokens, and password_reset_tokens tables in backend/alembic/versions/
- [ ] T009 Create Pydantic request/response schemas for auth operations in backend/app/schemas/auth.py (RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, TokenRefreshResponse, AuthResponse)
- [ ] T010 [P] Create Pydantic request/response schemas for user/address operations in backend/app/schemas/user.py (UserResponse, UserUpdateRequest, AddressResponse, AddressCreateRequest, AddressUpdateRequest)
- [ ] T011 Add get_current_user dependency (decode JWT from access_token cookie, return User or raise 401) to backend/app/core/deps.py
- [ ] T012 Configure rate limiting with slowapi (20 req/min/IP) as FastAPI middleware in backend/app/main.py
- [ ] T013 Configure CORS middleware with allow_credentials=True and explicit origins from CORS_ORIGINS env var in backend/app/main.py
- [ ] T014 Create email sender interface (EmailSender protocol) with ConsoleEmailSender implementation in backend/app/services/email_service.py
- [ ] T015 Add 401-to-refresh interceptor in frontend/src/lib/api-client.ts (on 401, attempt POST /api/v1/auth/refresh, retry original request; if refresh also fails, redirect to /login)

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 — Register a New Account (Priority: P1) MVP

**Goal**: A visitor can create an account with email/password, be automatically logged in, and redirected to the homepage with a welcome notification.

**Independent Test**: Fill out the registration form with valid data, submit, verify user is logged in and can access protected pages.

### Implementation for User Story 1

- [ ] T016 [US1] Implement register function in backend/app/services/auth_service.py (validate email uniqueness case-insensitive, hash password with bcrypt, create User with role=customer, generate access + refresh tokens, set httpOnly cookies)
- [ ] T017 [US1] Implement POST /api/v1/auth/register endpoint in backend/app/api/v1/auth.py per contracts/auth.md (call auth_service.register, return 201 with user data, handle 409 duplicate email, 422 validation errors)
- [ ] T018 [US1] Create registration page with form (email, password, first_name, last_name), real-time password strength indicator, and client-side zod validation in frontend/src/pages/register.tsx
- [ ] T019 [US1] Create password strength indicator component in frontend/src/components/password-strength.tsx (displays strength level in real-time as user types)
- [ ] T020 [US1] Create useAuth hook in frontend/src/hooks/use-auth.ts (register function that calls POST /api/v1/auth/register, manages user state via GET /api/v1/users/me query)
- [ ] T021 [US1] Wire register page: on successful registration, redirect to homepage and display welcome toast notification in frontend/src/pages/register.tsx
- [ ] T022 [US1] Add /register route to frontend/src/App.tsx

**Checkpoint**: Registration flow is fully functional. A visitor can create an account and be logged in.

---

## Phase 4: User Story 2 — Log In and Log Out (Priority: P1)

**Goal**: A registered user can log in with email/password, access protected pages, and log out to end their session.

**Independent Test**: Log in with valid credentials, verify access to a protected page; log out, verify protected pages redirect to login.

### Implementation for User Story 2

- [ ] T023 [US2] Implement login function in backend/app/services/auth_service.py (verify password, check lockout state, increment failed_login_count on failure, reset on success, generate tokens, set cookies)
- [ ] T024 [US2] Implement logout function in backend/app/services/auth_service.py (revoke refresh token, clear cookies)
- [ ] T025 [US2] Implement token refresh function in backend/app/services/auth_service.py (validate refresh token hash, check not revoked/expired, issue new access token cookie)
- [ ] T026 [US2] Implement POST /api/v1/auth/login endpoint in backend/app/api/v1/auth.py per contracts/auth.md (handle 401 invalid credentials, 423 account locked, 429 rate limit)
- [ ] T027 [P] [US2] Implement POST /api/v1/auth/logout endpoint in backend/app/api/v1/auth.py per contracts/auth.md (requires authentication, clears cookies)
- [ ] T028 [P] [US2] Implement POST /api/v1/auth/refresh endpoint in backend/app/api/v1/auth.py per contracts/auth.md (read refresh_token cookie, return new access_token cookie or 401)
- [ ] T029 [US2] Add login and logout functions to frontend/src/hooks/use-auth.ts (login calls POST /api/v1/auth/login, logout calls POST /api/v1/auth/logout, both invalidate user query)
- [ ] T030 [US2] Create login page with form (email, password), "Forgot password?" link, error display, and redirect-after-login logic in frontend/src/pages/login.tsx
- [ ] T031 [US2] Create ProtectedRoute component in frontend/src/components/protected-route.tsx (wraps pages requiring auth, redirects to /login if useAuth returns unauthenticated)
- [ ] T032 [US2] Create UserMenu component in frontend/src/components/user-menu.tsx (shows Login/Register links when unauthenticated; shows user name + Logout action when authenticated)
- [ ] T033 [US2] Add /login route and wrap protected pages with ProtectedRoute in frontend/src/App.tsx

**Checkpoint**: Login/logout flow is fully functional. Users can authenticate, access protected pages, and securely end sessions.

---

## Phase 5: User Story 3 — Reset Forgotten Password (Priority: P2)

**Goal**: A registered user who forgot their password can request a reset link via email, use it to set a new password, and log in with the new password.

**Independent Test**: Request a reset for a known email, use the token to set a new password, verify login works with the new password.

### Implementation for User Story 3

- [ ] T034 [US3] Implement forgot_password function in backend/app/services/auth_service.py (generate token via secrets.token_urlsafe(32), store SHA-256 hash in password_reset_tokens, invalidate previous tokens for user, send reset email via email_service)
- [ ] T035 [US3] Implement reset_password function in backend/app/services/auth_service.py (hash incoming token, look up valid non-expired non-used token, set new hashed password, mark token used, revoke all refresh tokens per FR-014)
- [ ] T036 [US3] Implement POST /api/v1/auth/forgot-password endpoint in backend/app/api/v1/auth.py per contracts/auth.md (always return "If an account exists, a reset link has been sent" — no email enumeration)
- [ ] T037 [US3] Implement POST /api/v1/auth/reset-password endpoint in backend/app/api/v1/auth.py per contracts/auth.md (handle 400 invalid/expired token, 422 validation errors)
- [ ] T038 [US3] Create forgot password page with email input in frontend/src/pages/forgot-password.tsx (submit shows success message regardless of email existence)
- [ ] T039 [US3] Create reset password page with new password input and password strength indicator in frontend/src/pages/reset-password.tsx (reads token from URL query param, on success redirects to /login with success message)
- [ ] T040 [US3] Add /forgot-password and /reset-password routes to frontend/src/App.tsx

**Checkpoint**: Password reset flow is end-to-end functional. Locked-out or forgetful users can regain access.

---

## Phase 6: User Story 4 — View and Edit Profile (Priority: P2)

**Goal**: A logged-in user can view their profile (email read-only, first name, last name, phone) and update editable fields.

**Independent Test**: Navigate to profile page, change last name, save, refresh, verify change persisted.

### Implementation for User Story 4

- [ ] T041 [US4] Implement get_profile and update_profile functions in backend/app/services/user_service.py (get user by ID from auth, partial update of first_name/last_name/phone)
- [ ] T042 [US4] Implement GET /api/v1/users/me endpoint in backend/app/api/v1/users.py per contracts/users.md (requires authentication, return user profile)
- [ ] T043 [US4] Implement PATCH /api/v1/users/me endpoint in backend/app/api/v1/users.py per contracts/users.md (requires authentication, partial update, return updated profile)
- [ ] T044 [US4] Create profile page with form (email read-only, editable first_name, last_name, phone) and success toast on save in frontend/src/pages/profile.tsx
- [ ] T045 [US4] Add /profile route (wrapped in ProtectedRoute) to frontend/src/App.tsx

**Checkpoint**: Profile viewing and editing is functional. Authenticated users can manage their basic information.

---

## Phase 7: User Story 5 — Manage Saved Addresses (Priority: P3)

**Goal**: A logged-in user can add, edit, delete, and set default shipping addresses (up to 5).

**Independent Test**: Create an address, edit it, mark another as default, delete the first, verify state after each operation.

### Implementation for User Story 5

- [ ] T046 [US5] Implement address CRUD functions in backend/app/services/user_service.py (list addresses, create with 5-max check, update, delete with default auto-promotion per research R-009)
- [ ] T047 [US5] Implement GET /api/v1/users/me/addresses endpoint in backend/app/api/v1/users.py per contracts/users.md (requires authentication, return address list)
- [ ] T048 [P] [US5] Implement POST /api/v1/users/me/addresses endpoint in backend/app/api/v1/users.py per contracts/users.md (requires authentication, handle 400 address limit)
- [ ] T049 [P] [US5] Implement PATCH /api/v1/users/me/addresses/:id endpoint in backend/app/api/v1/users.py per contracts/users.md (requires authentication, handle 404, partial update, default flag logic)
- [ ] T050 [P] [US5] Implement DELETE /api/v1/users/me/addresses/:id endpoint in backend/app/api/v1/users.py per contracts/users.md (requires authentication, handle 404, auto-promote default)
- [ ] T051 [US5] Create useAddresses hook in frontend/src/hooks/use-addresses.ts (TanStack Query hooks for list, create, update, delete address operations)
- [ ] T052 [US5] Create reusable address form component in frontend/src/components/address-form.tsx (label, street_line_1, street_line_2, city, state, postal_code, country, is_default checkbox; used for both create and edit)
- [ ] T053 [US5] Create addresses management page in frontend/src/pages/addresses.tsx (list addresses, add/edit/delete actions, default badge, max 5 indicator)
- [ ] T054 [US5] Add /addresses route (wrapped in ProtectedRoute) to frontend/src/App.tsx

**Checkpoint**: Address management is fully functional. Users can manage up to 5 addresses with default promotion.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [ ] T055 [P] Add auth routes to FastAPI router registry and verify OpenAPI docs include all auth/user endpoints in backend/app/main.py
- [ ] T056 [P] Add SmtpEmailSender implementation to backend/app/services/email_service.py (uses aiosmtplib, configurable via SMTP_* env vars, injectable via dependency)
- [ ] T057 Wire UserMenu component into the site header/navigation layout so it appears on all pages in frontend/src/App.tsx or shared layout component
- [ ] T058 Run quickstart.md validation: start the stack, execute all curl commands from quickstart.md, verify expected responses

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **User Stories (Phases 3–7)**: All depend on Phase 2 completion
  - US1 and US2 can proceed in parallel (both P1, share foundational infrastructure)
  - US3 depends on US2 (login must exist to verify password reset works end-to-end)
  - US4 can start after Phase 2 (independent of US1–US3, only needs auth middleware)
  - US5 can start after Phase 2 (independent, only needs auth middleware)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 — Register (P1)**: Can start after Phase 2. No dependencies on other stories.
- **US2 — Login/Logout (P1)**: Can start after Phase 2. No dependencies on other stories. Can run in parallel with US1.
- **US3 — Reset Password (P2)**: Depends on US2 (login endpoint needed to verify new password works). Can run in parallel with US4/US5.
- **US4 — View/Edit Profile (P2)**: Can start after Phase 2. No dependencies on other stories. Can run in parallel with US1–US3/US5.
- **US5 — Manage Addresses (P3)**: Can start after Phase 2. No dependencies on other stories. Can run in parallel with US1–US4.

### Within Each User Story

- Backend service logic before endpoints
- Backend endpoints before frontend pages
- Frontend hooks before pages that use them
- All tasks within a story should be completed before the checkpoint

### Parallel Opportunities

- T003 and T004 can run in parallel (different frontend files)
- T006 and T007 can run in parallel (different backend model files)
- T009 and T010 can run in parallel (different schema files)
- US1 and US2 can run in parallel after Phase 2
- US4 and US5 can run in parallel after Phase 2
- T027 and T028 can run in parallel (different endpoints, same file but independent functions)
- T048, T049, T050 can run in parallel (independent CRUD endpoints)

---

## Parallel Example: User Story 1 (Register)

```bash
# After Phase 2 is complete, launch US1 implementation:
Task T016: "Implement register function in backend/app/services/auth_service.py"
  → then T017: "Implement POST /api/v1/auth/register endpoint in backend/app/api/v1/auth.py"

# In parallel (different files):
Task T019: "Create password strength indicator component in frontend/src/components/password-strength.tsx"
Task T020: "Create useAuth hook in frontend/src/hooks/use-auth.ts"

# After backend + frontend hooks ready:
Task T018: "Create registration page in frontend/src/pages/register.tsx"
  → then T021: "Wire register page redirect and toast"
  → then T022: "Add /register route"
```

## Parallel Example: User Story 5 (Addresses)

```bash
# Backend CRUD endpoints can be built in parallel:
Task T048: "POST /api/v1/users/me/addresses"
Task T049: "PATCH /api/v1/users/me/addresses/:id"
Task T050: "DELETE /api/v1/users/me/addresses/:id"

# Frontend in parallel:
Task T051: "Create useAddresses hook"
Task T052: "Create address form component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1 — Register
4. **STOP and VALIDATE**: Register a user, verify they are logged in and can access protected pages
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Register) → Test independently → MVP!
3. Add US2 (Login/Logout) → Test independently → Core auth complete
4. Add US3 (Reset Password) → Test independently → Self-service account recovery
5. Add US4 (Profile) → Test independently → User self-management
6. Add US5 (Addresses) → Test independently → Checkout-ready address book
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Register) + US3 (Reset Password)
   - Developer B: US2 (Login/Logout) + US4 (Profile)
   - Developer C: US5 (Addresses)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

# Implementation Plan: Authentication & User Management

**Branch**: `000-specifications` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-auth-user-management/spec.md`

## Summary

Authentication & User Management provides the foundational identity layer for the ecommerce application. It covers email/password registration, JWT-based session management (access + refresh tokens in httpOnly cookies), login with brute-force protection (account lockout), password reset via email, user profile editing, and saved address management. The implementation follows the established frontend/backend separation: a FastAPI backend serving auth and user REST endpoints consumed by a React + TypeScript frontend using TanStack Query for auth state.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, passlib[bcrypt], python-jose[cryptography], slowapi (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod (frontend)
**Storage**: PostgreSQL 16+
**Testing**: pytest + httpx (backend integration tests); Vitest + Testing Library (frontend component tests)
**Target Platform**: Linux server (backend), modern browsers (frontend)
**Project Type**: Web application (frontend SPA + backend API)
**Performance Goals**: < 200ms p95 API reads, < 500ms p95 API writes (including bcrypt hashing), < 2.5s LCP frontend
**Constraints**: httpOnly cookies for token transport, bcrypt for password hashing, rate limiting on auth endpoints (20 req/min/IP), no SELECT *
**Scale/Scope**: 10,000+ registered users, 5 addresses per user, 7-day refresh token window

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Architecture (frontend/backend separation) | PASS | Separate React SPA and FastAPI API communicating via REST JSON. Auth state derived from API calls, not shared state. |
| II. Technology Stack | PASS | All mandated technologies used. Added passlib[bcrypt], python-jose, slowapi as auth-specific backend dependencies. |
| III. Code Quality | PASS | Pydantic schemas for all auth/user endpoints, Alembic migrations for User/Address/Token tables, zod validation for frontend forms, TS strict mode, ruff + mypy. |
| IV. Testing Standards | PASS | pytest + httpx for auth/user API tests, Vitest + Testing Library for auth/profile pages. Auth is a critical flow → e2e tests required. |
| V. Security | PASS | bcrypt password hashing, SQLAlchemy ORM (no raw SQL), auth required for all data-modifying endpoints except register/login/forgot-password, CORS restricted, rate limiting on auth endpoints. |
| VI. API Design | PASS | RESTful /api/v1/auth/*, /api/v1/users/*, consistent error format with detail + code, cursor-based pagination not needed (address list is max 5). |
| VII. Database | PASS | UUIDs for all PKs, created_at/updated_at on all tables, hard deletes for ephemeral data (tokens, addresses), FK constraints, indexes on FKs and query columns. |
| VIII. Performance | PASS | < 200ms p95 reads, < 500ms p95 writes (bcrypt adds ~250ms), no SELECT *. |
| IX. Developer Experience | PASS | docker compose up, .env for JWT_SECRET_KEY and SMTP config, FastAPI OpenAPI docs, independent FE/BE dev. |

**Gate result**: ALL PASS — proceeding to Phase 0.

**Post-Phase 1 re-check**: ALL PASS — no new violations introduced during design. The data model, API contracts, and project structure all comply with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-user-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── auth.md          # Auth endpoints (register, login, logout, refresh, forgot/reset password)
│   └── users.md         # User profile and address endpoints
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py              # Auth endpoints (register, login, logout, refresh, forgot/reset password)
│   │       └── users.py             # User profile and address endpoints
│   ├── models/
│   │   ├── user.py                  # User, Address SQLAlchemy models
│   │   └── token.py                 # RefreshToken, PasswordResetToken models
│   ├── schemas/
│   │   ├── auth.py                  # Auth request/response Pydantic schemas
│   │   └── user.py                  # User/address Pydantic schemas
│   ├── services/
│   │   ├── auth_service.py          # Auth business logic (hashing, tokens, lockout)
│   │   ├── user_service.py          # Profile and address business logic
│   │   └── email_service.py         # Email sender interface + console/SMTP implementations
│   ├── core/
│   │   ├── config.py                # Settings from .env (existing, extended with JWT/SMTP vars)
│   │   ├── database.py              # Async SQLAlchemy engine/session (existing)
│   │   ├── deps.py                  # Dependency injection (existing, add get_current_user)
│   │   ├── security.py              # JWT encode/decode, password hash/verify utilities
│   │   └── pagination.py            # Cursor-based pagination utility (existing)
│   └── main.py                      # FastAPI app entry point (existing, add auth middleware)
├── alembic/
│   └── versions/
│       └── xxxx_add_auth_tables.py  # Migration: users, addresses, refresh_tokens, password_reset_tokens
├── tests/
│   ├── conftest.py                  # Test fixtures (existing, add auth helpers)
│   ├── test_auth.py                 # Auth endpoint integration tests
│   └── test_users.py               # User/address endpoint integration tests
└── ...                              # Existing files from 001-product-catalog

frontend/
├── src/
│   ├── components/
│   │   ├── protected-route.tsx      # Route guard for authenticated pages
│   │   ├── user-menu.tsx            # Header user menu (login/register or profile/logout)
│   │   ├── password-strength.tsx    # Real-time password strength indicator
│   │   └── address-form.tsx         # Reusable address form component
│   ├── pages/
│   │   ├── login.tsx                # Login page
│   │   ├── register.tsx             # Registration page
│   │   ├── forgot-password.tsx      # Forgot password request page
│   │   ├── reset-password.tsx       # Reset password form (with token from URL)
│   │   ├── profile.tsx              # User profile page
│   │   └── addresses.tsx            # Saved addresses management page
│   ├── hooks/
│   │   ├── use-auth.ts              # Auth state hook (current user, isAuthenticated, login, logout, register)
│   │   └── use-addresses.ts         # TanStack Query hooks for addresses API
│   ├── lib/
│   │   ├── api-client.ts            # Fetch wrapper (existing, add 401 → refresh interceptor)
│   │   ├── types.ts                 # Shared TypeScript types (existing, add User, Address types)
│   │   ├── validations.ts           # Zod schemas for auth/profile forms
│   │   └── utils.ts                 # Utilities (existing)
│   └── App.tsx                      # Add auth routes and ProtectedRoute wrapper
├── tests/
│   ├── login.test.tsx
│   ├── register.test.tsx
│   ├── profile.test.tsx
│   └── addresses.test.tsx
└── ...                              # Existing files from 001-product-catalog
```

**Structure Decision**: Extends the existing web application layout from 001-product-catalog. New auth-specific files are added to the established `backend/app/` and `frontend/src/` directories. The `core/security.py` module centralizes JWT and password hashing utilities. The `services/email_service.py` uses a protocol pattern for pluggable email delivery. No structural changes to existing files beyond extending `config.py`, `deps.py`, `api-client.ts`, and `types.ts`.

## Complexity Tracking

No constitution violations — this section is not applicable.

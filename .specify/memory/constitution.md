<!--
  Sync Impact Report
  ===================
  Version change: 0.0.0 → 1.0.0 (initial ratification)

  Modified principles: N/A (first version)

  Added sections:
  - Core Principles (7 principles: Type Safety, Shared Validation, Security by Default,
    Data Integrity, Test-Driven Quality, Monorepo Discipline, Simplicity & Scope Control)
  - Technology & Architecture Constraints
  - Development Workflow & Quality Gates
  - Governance

  Removed sections: N/A (first version)

  Templates requiring updates:
  - .specify/templates/plan-template.md — ✅ reviewed (Constitution Check section aligns)
  - .specify/templates/spec-template.md — ✅ reviewed (scope/requirements sections align)
  - .specify/templates/tasks-template.md — ✅ reviewed (phased structure supports principles)
  - .specify/templates/checklist-template.md — ✅ reviewed (category structure compatible)

  Follow-up TODOs: None
-->

# Eshopy Constitution

## Core Principles

### I. End-to-End Type Safety (NON-NEGOTIABLE)

TypeScript strict mode MUST be enabled in every workspace (`apps/web`, `apps/api`, `packages/shared`).
No `any` types are permitted unless absolutely unavoidable, and each instance MUST include a
comment explaining why. Named exports MUST be used everywhere except Next.js pages (which require
default exports). All data crossing a boundary — API request/response, database query result,
form input — MUST be typed. This ensures compile-time guarantees across the entire stack and
eliminates an entire class of runtime errors.

### II. Shared Validation — Single Source of Truth

All input validation schemas MUST be defined using Zod. Schemas used by both frontend and backend
MUST live in `packages/shared/` and be imported from there. Validation logic MUST NOT be duplicated
between apps. API endpoints MUST apply Zod middleware at the boundary. Frontend forms MUST use
React Hook Form with Zod resolvers referencing the same shared schemas. This principle eliminates
drift between client-side and server-side validation and guarantees consistent error messages.

### III. Security by Default (NON-NEGOTIABLE)

- JWT access tokens (15 min TTL) and refresh tokens (7 days TTL) MUST be stored in httpOnly,
  secure, sameSite=strict cookies. Tokens MUST NEVER be stored in localStorage or exposed to
  client JavaScript.
- Card payment data MUST NEVER touch the server. All payment UI MUST use Stripe.js and React
  Stripe Elements exclusively.
- Passwords MUST be hashed with bcrypt (12 salt rounds). Rate limiting (Redis-backed) MUST be
  applied to authentication, registration, and password reset endpoints.
- All API endpoints MUST validate and sanitize inputs via Zod middleware. Rich-text content MUST
  be sanitized with DOMPurify before rendering.
- Helmet.js MUST be applied for HTTP security headers. CORS MUST be restricted to the frontend
  origin. Stripe webhook signatures MUST be verified.
- Secrets and credentials MUST NEVER be committed to the repository. All secrets MUST be managed
  via environment variables.

### IV. Data Integrity & Soft-Delete

- Products and user accounts MUST use the soft-delete pattern (`is_active` flag). No production
  data MUST be permanently deleted in v1.
- Order items MUST store snapshots of product name, variant name, and unit price at the time of
  purchase. Shipping addresses on orders MUST be stored as JSON snapshots, not foreign key
  references. Historical orders MUST remain accurate regardless of future catalog or address changes.
- Stock quantity decrements MUST be atomic:
  `UPDATE ... SET stock_quantity = stock_quantity - $qty WHERE stock_quantity >= $qty`.
  Stock MUST be validated both when an item is added to the cart AND again at checkout.
  Two customers MUST NEVER be able to purchase the last unit of the same item simultaneously.
- At least one admin account MUST always exist. The system MUST prevent demotion of the last admin.
- Every order status change MUST be logged in `OrderStatusLog` with admin identity and timestamp.

### V. Prisma-Only Database Access

All database access MUST go through Prisma ORM. Raw SQL MUST NOT be used unless absolutely
necessary (and MUST be justified with a comment). This ensures parameterized queries by default
(preventing SQL injection), type-safe database operations, and consistent migration management.
PostgreSQL full-text search (`tsvector`/`tsquery`) is the one area where Prisma's raw query
escape hatch is acceptable for search indexing.

### VI. Test-Driven Quality

- Unit tests (Vitest) MUST achieve at least 80% line coverage for controllers and services.
  External dependencies (Prisma, Stripe, S3, Redis) MUST be mocked.
- Integration tests (Vitest + Supertest) MUST cover API endpoints with a real PostgreSQL
  database in Docker. Each test suite MUST start with a clean database state.
- E2E tests (Playwright) MUST cover critical user journeys: guest-to-checkout, search-to-review,
  and admin product/order management.
- Test files MUST be co-located with source files: `foo.ts` -> `foo.test.ts`.
- `pnpm test`, `pnpm lint`, and `pnpm typecheck` MUST pass before any work is considered complete.

### VII. Simplicity & Scope Control

- Start simple. Do not build abstractions or infrastructure for features that are explicitly
  out of scope for v1 (see GOAL_clarified.md Section 3 — "Explicitly Out of Scope").
- Use React Context only for lightweight client UI state (auth, cart UI, theme). Server state
  MUST be managed with TanStack React Query v5. `useEffect` MUST NOT be used for data fetching.
- Use Tailwind CSS utility classes for all styling. Custom CSS MUST NOT be written unless
  Tailwind cannot express the requirement.
- Use `async`/`await` for all asynchronous code. `.then()` chains MUST NOT be used.
- Use `date-fns` for all date formatting and manipulation.
- Use `pino` for all backend logging. `console.log` MUST NOT appear in production code.
- Offset-based pagination MUST be used throughout: 20 items for product listings, 25 rows
  for admin tables.

## Technology & Architecture Constraints

### Stack (Locked for v1)

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | TypeScript (strict) | 5.x |
| Runtime | Node.js | 20 LTS |
| Backend | Express.js | 4.x |
| Frontend | Next.js (App Router) | 15 |
| UI | React | 19 |
| Database | PostgreSQL | 16 |
| ORM | Prisma | 6 |
| Cache / Rate Limiting | Redis | 7 |
| CSS | Tailwind CSS | 4 |
| Server State | TanStack React Query | 5 |
| Payment | Stripe (Payment Intents + Elements) | latest |
| Image Storage | AWS S3 + CloudFront CDN | latest |
| Monorepo | Turborepo + pnpm workspaces | pnpm 9+ |

### Architecture Pattern

Monorepo monolith with two apps (`apps/web`, `apps/api`) and one shared package
(`packages/shared`). The API serves REST JSON at `/api/v1/...` on port 4000. The frontend
runs on port 3000. All API errors MUST follow the standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": []
  }
}
```

### Image Uploads

Product images MUST be uploaded via S3 presigned URLs (frontend uploads directly to S3).
Images MUST NEVER be streamed through the API server. Maximum 10 images per product, 5 MB each.
Images are served via CloudFront CDN.

### Target Scale (v1)

- ~100 concurrent users
- ~10,000 products maximum
- API p95 response time < 500ms
- Initial page load < 3s, subsequent navigation < 1s
- Single-region (US), single-currency (USD)

## Development Workflow & Quality Gates

### Pre-Commit (Automated)

Husky + lint-staged MUST run ESLint and Prettier on staged files before every commit.

### CI Pipeline (GitHub Actions)

- **On pull request**: Lint -> Typecheck -> Unit/integration tests -> Build
- **On merge to main**: All PR checks + E2E tests -> Build Docker images -> Deploy

### Quality Gates

Every change MUST satisfy all of the following before merge:

1. `pnpm lint` passes with zero errors
2. `pnpm typecheck` passes with zero errors
3. `pnpm test` passes with all tests green
4. `pnpm build` succeeds for all affected workspaces
5. No `any` types added without justification
6. No Zod schema duplication between apps
7. No secrets or credentials in committed files
8. REST conventions followed: plural nouns, proper HTTP methods, correct status codes

### Deployment

Docker Compose on VPS with Nginx reverse proxy (Let's Encrypt SSL). Containers: Nginx,
Next.js, Express.js, PostgreSQL, Redis. Zero-downtime rolling restarts via SSH.

## Governance

This constitution is the authoritative reference for all architectural, security, and quality
decisions in the Eshopy project. It supersedes any conflicting guidance found elsewhere.

- **Compliance**: All code contributions MUST comply with every principle above. Reviewers
  MUST verify compliance during code review.
- **Amendments**: Changes to this constitution require documentation of the rationale, impact
  assessment on existing code, and a migration plan for any breaking changes. Version MUST be
  incremented according to semantic versioning (MAJOR for principle removals/redefinitions,
  MINOR for new principles or material expansions, PATCH for clarifications and wording).
- **Scope reference**: GOAL_clarified.md is the single source of truth for product scope.
  Features listed as "Explicitly Out of Scope for v1" MUST NOT be implemented unless the
  scope document is formally amended first.
- **CLAUDE.md alignment**: CLAUDE.md provides runtime development guidance consistent with
  this constitution. If a conflict arises, this constitution takes precedence.

**Version**: 1.0.0 | **Ratified**: 2026-04-17 | **Last Amended**: 2026-04-17

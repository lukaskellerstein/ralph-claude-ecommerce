# Eshopy — AI Agent Instructions

> Full-featured ecommerce web app (storefront + admin dashboard) built with TypeScript, Next.js, Express.js, and PostgreSQL.

---

## Technology Stack

- **Language**: TypeScript (strict mode) — frontend and backend
- **Runtime**: Node.js 20 LTS
- **Backend**: Express.js 4.x — REST API at `/api/v1/`
- **Frontend**: Next.js 15 (App Router) + React 19
- **Database**: PostgreSQL 16 via Prisma v6
- **Cache**: Redis 7 (caching, rate limiting, JWT blacklisting)
- **Styling**: Tailwind CSS v4
- **State**: TanStack React Query v5 (server state) + React Context (UI state)
- **Payment**: Stripe (Payment Intents API + webhooks + React Stripe Elements)
- **Storage**: AWS S3 (presigned URLs) + CloudFront CDN
- **Forms**: React Hook Form + Zod
- **Validation**: Zod (shared schemas in `packages/shared/`)
- **Testing**: Vitest (unit/integration) + Playwright (e2e)
- **Monorepo**: Turborepo + pnpm 9+ workspaces
- **CI/CD**: GitHub Actions
- **Logging**: pino
- **Linting**: ESLint + Prettier + Husky + lint-staged

---

## Architecture

**Pattern**: Monorepo monolith — single repo, two apps, shared packages.

```
eshopy/
├── apps/
│   ├── web/                  # Next.js frontend (storefront + admin)
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Client utilities
│   │   └── styles/           # Global styles
│   └── api/                  # Express.js backend
│       ├── src/
│       │   ├── routes/       # REST route handlers
│       │   ├── controllers/  # Business logic
│       │   ├── middleware/   # Auth, validation, error handling
│       │   ├── services/     # External integrations (Stripe, S3, email)
│       │   └── utils/        # Shared utilities
│       └── prisma/
│           ├── schema.prisma
│           ├── migrations/
│           └── seed.ts
├── packages/
│   └── shared/               # Shared types, Zod schemas, constants
├── docker-compose.yml        # Dev infrastructure
├── docker-compose.prod.yml   # Production stack
├── Dockerfile
└── turbo.json
```

### Key Constraints

- API serves REST JSON at `/api/v1/...` on port 4000. Frontend on port 3000.
- Use Zod schemas from `packages/shared/` for both frontend and backend validation. Never duplicate validation logic.
- Use Prisma for all database access. Never write raw SQL unless absolutely necessary.
- All API errors must follow this format:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable message",
      "details": []
    }
  }
  ```
- JWT access tokens (15 min) and refresh tokens (7 days) stored in httpOnly, secure, sameSite=strict cookies. Never store tokens in localStorage.
- Card payment data must never touch the server. Use Stripe.js / React Stripe Elements exclusively.
- Product images uploaded via S3 presigned URLs (frontend → S3 direct). Max 10 images per product, 5 MB each.
- Soft-delete pattern: products and users are deactivated, never permanently deleted.
- Order items store snapshots of product name, variant name, and unit price at time of purchase.
- Shipping address on orders is a JSON snapshot, not a foreign key reference.
- Stock decrement must be atomic: `UPDATE ... SET stock_quantity = stock_quantity - $qty WHERE stock_quantity >= $qty`.

---

## Commands

```bash
# Install
pnpm install

# Dev infrastructure
docker compose up -d

# Database
pnpm --filter api prisma migrate dev      # Run migrations
pnpm --filter api prisma db seed           # Seed database

# Development
pnpm dev                                   # Start all apps
pnpm --filter api dev                      # Backend only
pnpm --filter web dev                      # Frontend only

# Build
pnpm build                                 # Build all
pnpm --filter api build                    # Backend only
pnpm --filter web build                    # Frontend only

# Test
pnpm test                                  # Unit + integration
pnpm test:watch                            # Watch mode
pnpm test:coverage                         # With coverage
pnpm test:e2e                              # E2E (needs running env)

# Quality
pnpm lint                                  # ESLint
pnpm typecheck                             # TypeScript checking

# Production
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

## Code Style

- Use TypeScript strict mode everywhere. No `any` types unless absolutely unavoidable (and add a comment explaining why).
- Use named exports, not default exports (except for Next.js pages which require default exports).
- Place test files co-located with source: `foo.ts` → `foo.test.ts`.
- Use Zod schemas for all input validation. Define schemas in `packages/shared/` when used by both frontend and backend.
- Use React Hook Form for all forms.
- Use TanStack React Query for all API data fetching on the frontend. Do not use `useEffect` for data fetching.
- Use React Context only for lightweight client UI state (auth, cart UI, theme). Never use it for server-state.
- Use Tailwind CSS utility classes. Do not write custom CSS unless Tailwind cannot express it.
- Use `date-fns` for all date formatting and manipulation.
- Use pino for all backend logging. Never use `console.log` in production code.
- Use async/await, not `.then()` chains.
- Always validate and sanitize inputs at the API boundary (Zod middleware).
- Rich-text content must be sanitized with DOMPurify before rendering.
- Follow REST conventions: plural nouns for resources, proper HTTP methods and status codes.
- Offset-based pagination: 20 items for product listings, 25 rows for admin tables.

---

## Testing

- **Unit tests (Vitest)**: ≥80% line coverage for controllers and services. Mock external dependencies (Prisma, Stripe, S3, Redis).
- **Integration tests (Vitest + Supertest)**: Test API endpoints with real PostgreSQL (Docker). Clean DB state per suite.
- **E2E tests (Playwright)**: Cover critical flows — guest→register→checkout, search→filter→review, admin product/order management.
- Always write tests for new business logic. Run `pnpm test` before considering work complete.
- Run `pnpm lint` and `pnpm typecheck` before considering work complete.

---

## Deployment

- **Target**: Docker Compose on VPS with Nginx reverse proxy (Let's Encrypt SSL).
- **CI/CD**: GitHub Actions — PR: lint + typecheck + test + build. Merge to main: + e2e + deploy.
- **Containers**: Nginx, Next.js, Express.js, PostgreSQL, Redis.
- All secrets via environment variables. Never commit `.env` files, API keys, or credentials.

---

## Key Rules

- Never commit code to git unless explicitly asked to.
- Never permanently delete data. Use soft-delete (is_active flags) for products and users.
- Never handle card data server-side. Stripe Elements only.
- Never use raw SQL. Use Prisma queries.
- Never store JWT tokens in localStorage. Use httpOnly cookies only.
- Never duplicate Zod schemas between frontend and backend. Share from `packages/shared/`.
- Always validate stock at add-to-cart AND at checkout. Always decrement stock atomically.
- Always return consistent error response format from the API.
- Always use presigned URLs for S3 uploads (never stream through the API server).
- Always snapshot product/variant names and prices into OrderItem at purchase time.
- Always log admin actions on order status changes (OrderStatusLog).
- Always ensure at least one admin account exists before demoting an admin.

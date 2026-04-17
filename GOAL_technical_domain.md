# Eshopy — Technical Domain Specification

This document captures the complete technical-level decisions for Eshopy v1, derived from the product domain specification and subsequent technical clarification.

---

## 1. Technology Stack

### Language
- **TypeScript** (strict mode) — used across both frontend and backend for end-to-end type safety.
- **Node.js** v20 LTS — runtime for the backend API server.

### Backend
- **Express.js** v4 — HTTP framework for the REST API server.
- **Prisma** v6 — ORM for database access, migrations, and type-safe queries.
- **PostgreSQL** 16 — primary relational database.
- **Redis** 7 — caching layer, rate limiting, and token blacklisting.

### Frontend
- **Next.js** 15 (App Router) — React-based framework with SSR/SSG for SEO and performance.
- **React** 19 — UI library.
- **Tailwind CSS** v4 — utility-first CSS framework for styling.
- **TanStack React Query** v5 — server state management (API data fetching, caching, mutations).
- **React Context** — lightweight client-side UI state (auth state, cart UI, theme).

### Key Libraries
| Purpose | Library | Version |
|---------|---------|---------|
| Payment processing | Stripe Node SDK + Stripe.js + React Stripe Elements | latest |
| Image upload (S3) | @aws-sdk/client-s3 + presigned URLs | v3 |
| Rich text editor (admin) | TipTap or React Quill | latest |
| Form handling | React Hook Form + Zod | latest |
| API validation | Zod (shared schemas between frontend and backend) | latest |
| HTTP client (frontend) | Axios or native fetch via React Query | latest |
| Date handling | date-fns | latest |
| Password hashing | bcrypt | latest |
| JWT | jsonwebtoken | latest |
| Email (password reset) | Nodemailer (with SMTP provider, e.g., SendGrid or Mailgun) | latest |
| Rate limiting | rate-limiter-flexible (backed by Redis) | latest |
| Logging | pino | latest |
| Admin charts | Recharts | latest |
| Drag and drop (admin) | @dnd-kit | latest |

---

## 2. Architecture

### Pattern: Monorepo Monolith

A single repository containing both the frontend and backend applications with shared code.

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
│       │   ├── services/     # External service integrations (Stripe, S3, email)
│       │   └── utils/        # Shared utilities
│       └── prisma/
│           ├── schema.prisma # Database schema
│           ├── migrations/   # Database migrations
│           └── seed.ts       # Seed script (initial admin, categories, sample data)
├── packages/
│   └── shared/               # Shared TypeScript types, Zod schemas, constants
├── docker-compose.yml        # Local dev: PostgreSQL, Redis, (optional) MinIO for S3
├── Dockerfile                # Production multi-stage build
├── turbo.json                # Turborepo configuration
└── package.json              # Root workspace config
```

### Monorepo Tooling
- **Turborepo** — build orchestration, task caching, and dependency management across workspaces.
- **pnpm** — fast, disk-efficient package manager with native workspace support.

### API Pattern: REST

- RESTful JSON API served by Express.js on a dedicated port (e.g., `localhost:4000`).
- Next.js frontend communicates with the API via HTTP (server-side and client-side).
- API versioning: `/api/v1/...` prefix for all endpoints.
- Standard HTTP status codes and consistent error response format:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Human-readable message",
      "details": [{ "field": "email", "message": "Invalid email format" }]
    }
  }
  ```

### Key API Resource Groups
| Resource | Base Path | Notes |
|----------|-----------|-------|
| Auth | `/api/v1/auth` | Register, login, logout, refresh, forgot/reset password |
| Users | `/api/v1/users` | Profile, addresses (admin: user management) |
| Products | `/api/v1/products` | Catalog, search, filtering, sorting |
| Categories | `/api/v1/categories` | Category tree CRUD |
| Cart | `/api/v1/cart` | Server-side cart for authenticated users |
| Orders | `/api/v1/orders` | Order placement, history, cancellation |
| Reviews | `/api/v1/products/:id/reviews` | Product reviews CRUD |
| Wishlist | `/api/v1/wishlist` | Wishlist management |
| Admin | `/api/v1/admin/*` | Admin-specific endpoints (dashboard, management) |
| Upload | `/api/v1/upload` | S3 presigned URL generation for image uploads |
| Settings | `/api/v1/settings` | Store settings (tax rate, shipping prices) |

---

## 3. Authentication & Security

### JWT Strategy
- **Access token**: Short-lived (15 minutes), stored in an httpOnly, secure, sameSite cookie.
- **Refresh token**: Long-lived (7 days), stored in an httpOnly, secure, sameSite cookie on a separate path (`/api/v1/auth/refresh`).
- **Token refresh**: Silent refresh via the refresh endpoint. Frontend interceptor handles 401 responses by attempting a refresh before failing.
- **Logout**: Blacklist the refresh token in Redis (TTL = remaining token lifetime).

### Security Measures
- **Password hashing**: bcrypt with 12 salt rounds.
- **Rate limiting**: Redis-backed rate limiter on login (5 attempts per 15 minutes per email), registration, and password reset endpoints.
- **Account lockout**: 30-minute lockout after 5 failed login attempts (tracked in Redis).
- **CORS**: Configured to allow only the frontend origin.
- **Helmet.js**: Standard HTTP security headers.
- **Input validation**: Zod schemas applied as Express middleware on all endpoints.
- **SQL injection protection**: Prisma parameterized queries (no raw SQL unless absolutely necessary).
- **XSS protection**: React's built-in escaping + DOMPurify for rich-text content rendering.
- **CSRF protection**: httpOnly cookies with sameSite=strict mitigate CSRF; double-submit cookie pattern as backup.
- **Stripe webhook verification**: Validate webhook signatures using Stripe's SDK.

---

## 4. Infrastructure & Services

### Database: PostgreSQL 16
- Hosted in Docker container for local dev; managed PostgreSQL (e.g., DigitalOcean Managed Database) for production.
- **Full-text search**: PostgreSQL `tsvector`/`tsquery` with a GIN index on `product.name` and `product.description` columns.
- **Indexes**: On all foreign keys, slug fields, email, status fields, and search vectors.
- **Atomic stock decrement**: `UPDATE ... SET stock_quantity = stock_quantity - $qty WHERE stock_quantity >= $qty` with row-level locking to prevent overselling.

### Cache: Redis 7
- **Use cases**: API response caching (product listings, category tree), rate limiting, JWT blacklisting, account lockout tracking.
- **TTLs**: Product cache ~5 min, category tree ~30 min, rate limit windows as needed.
- Hosted in Docker container for local dev; managed Redis for production.

### Object Storage: AWS S3
- **Bucket**: Single bucket with folder prefixes per product (e.g., `products/{product_id}/{image_id}.webp`).
- **Upload flow**: Frontend requests a presigned URL from the API → uploads directly to S3 → sends the URL back to the API to save in the database.
- **CDN**: AWS CloudFront distribution in front of the S3 bucket for fast global image delivery.
- **Constraints**: Max 10 images per product, 5 MB each. Server-side validation of file type (JPEG, PNG, WebP) and size.

### Email: Nodemailer + SMTP Provider
- Used solely for password reset emails in v1.
- Provider: SendGrid, Mailgun, or similar SMTP relay (configurable via environment variables).

### Payment: Stripe
- **Stripe Checkout / Payment Intents API** for secure card processing.
- Card data handled entirely by Stripe.js / React Stripe Elements — never touches the server.
- **Webhook**: Listen for `payment_intent.succeeded` and `payment_intent.payment_failed` events to confirm order status.
- **Refunds**: Initiated via the Stripe Refunds API from admin or customer cancellation flows.

---

## 5. Build, Dev & Test Commands

### Prerequisites
- Node.js 20 LTS
- pnpm 9+
- Docker & Docker Compose (for PostgreSQL, Redis, and optional MinIO)

### Development

```bash
# Install dependencies
pnpm install

# Start infrastructure (PostgreSQL, Redis)
docker compose up -d

# Run database migrations
pnpm --filter api prisma migrate dev

# Seed database (creates initial admin, sample categories, products)
pnpm --filter api prisma db seed

# Start all apps in development mode (with hot reload)
pnpm dev

# Start only backend
pnpm --filter api dev

# Start only frontend
pnpm --filter web dev
```

### Build

```bash
# Build all packages and apps
pnpm build

# Build only backend
pnpm --filter api build

# Build only frontend
pnpm --filter web build
```

### Test

```bash
# Run all unit and integration tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with coverage
pnpm test:coverage

# Run e2e tests (requires running dev environment)
pnpm test:e2e

# Run linting
pnpm lint

# Run type checking
pnpm typecheck
```

### Docker (Production Build)

```bash
# Build production Docker image
docker compose -f docker-compose.prod.yml build

# Start production stack
docker compose -f docker-compose.prod.yml up -d
```

---

## 6. Testing Strategy

### Unit Tests (Vitest)
- **Scope**: Individual functions, utilities, Zod schemas, business logic in controllers/services.
- **Coverage target**: ≥80% line coverage for business logic (controllers, services).
- **Mocking**: Vitest built-in mocking for external dependencies (Prisma, Stripe, S3, Redis).
- **Location**: `*.test.ts` files co-located with source files.

### Integration Tests (Vitest + Supertest)
- **Scope**: API endpoint testing with a real test database (PostgreSQL in Docker).
- **Strategy**: Use Prisma to set up/tear down test data. Each test suite gets a clean database state.
- **Key areas**: Auth flows, order lifecycle (cart → checkout → payment → cancellation), stock management atomicity.

### End-to-End Tests (Playwright)
- **Scope**: Critical user journeys through the browser.
- **Key flows**:
  - Guest browsing → register → add to cart → checkout → order confirmation
  - Customer login → search/filter → product page → review submission
  - Admin login → product management → order status transitions
- **Environment**: Runs against a fully running dev stack (frontend + API + DB + Redis).
- **CI**: Runs in GitHub Actions with Docker Compose for infrastructure.

### Additional Quality Tools
- **ESLint** — code linting with TypeScript-aware rules.
- **Prettier** — code formatting.
- **Husky + lint-staged** — pre-commit hooks for linting and formatting.

---

## 7. Deployment

### Target: Docker + VPS

#### Production Architecture
```
                    ┌─────────────┐
                    │   Nginx     │  (reverse proxy, SSL termination)
                    │   :80/:443  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │                         │
     ┌────────▼────────┐     ┌─────────▼────────┐
     │   Next.js (web) │     │  Express.js (api) │
     │     :3000       │     │     :4000         │
     └─────────────────┘     └────────┬──────────┘
                                      │
                           ┌──────────┼──────────┐
                           │                     │
                  ┌────────▼──────┐    ┌─────────▼──────┐
                  │  PostgreSQL   │    │     Redis       │
                  │    :5432      │    │     :6379       │
                  └───────────────┘    └────────────────┘
```

#### Docker Compose (Production)
- **Nginx** container as reverse proxy with Let's Encrypt SSL (via certbot).
- **Next.js** container serving the frontend (production build with `next start`).
- **Express.js** container serving the API.
- **PostgreSQL** container (or managed database service).
- **Redis** container (or managed Redis service).

#### CI/CD: GitHub Actions
- **On pull request**: Lint → Type check → Unit/integration tests → Build.
- **On merge to main**: All PR checks + E2E tests → Build Docker images → Push to container registry (GitHub Container Registry or Docker Hub) → Deploy to VPS via SSH.
- **Deployment**: SSH into VPS → pull latest images → `docker compose up -d` with zero-downtime (rolling restart).

#### Environment Variables
All secrets and configuration managed via environment variables (`.env` files for local dev, injected via Docker/CI for production):
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `JWT_SECRET` — Secret for signing JWTs
- `JWT_REFRESH_SECRET` — Secret for refresh tokens
- `STRIPE_SECRET_KEY` — Stripe API secret key
- `STRIPE_PUBLISHABLE_KEY` — Stripe publishable key (frontend)
- `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` — S3 credentials
- `AWS_S3_BUCKET` — S3 bucket name
- `AWS_REGION` — AWS region
- `CLOUDFRONT_URL` — CloudFront distribution URL
- `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASS` — Email SMTP configuration
- `FRONTEND_URL` — Frontend origin (for CORS and email links)
- `NODE_ENV` — `development` | `production` | `test`

---

## 8. Non-Functional Requirements

### Performance Targets (Small Scale — v1)
| Metric | Target |
|--------|--------|
| Concurrent users | ~100 |
| API response time (p95) | <500ms |
| Page load time (initial) | <3s |
| Page load time (subsequent navigation) | <1s |
| Max product catalog size | ~10,000 products |
| Image upload size | ≤5 MB per image |
| Image count per product | ≤10 |

### Scalability
- v1 is designed for small-scale deployment on a single VPS.
- Stateless API design (JWT) allows horizontal scaling by adding more API containers behind a load balancer in future versions.
- PostgreSQL and Redis can be migrated to managed services for higher availability.

### Security
- All traffic over HTTPS (TLS 1.2+).
- Secrets never committed to the repository; managed via environment variables.
- Stripe PCI compliance via Stripe.js (card data never touches server).
- Regular dependency audits via `pnpm audit` in CI.
- httpOnly, secure, sameSite cookies for authentication tokens.
- Input validation on all API endpoints.
- Rate limiting on authentication and sensitive endpoints.

### Reliability
- Database backups: Daily automated pg_dump (cron job or managed DB backups).
- Docker health checks for all containers.
- Structured logging with pino for debugging and monitoring.
- Graceful shutdown handling in Express.js for zero-downtime deploys.

---

## 9. Technical Decisions Log

| Question | Decision |
|----------|----------|
| Backend framework | Node.js + Express.js (TypeScript) |
| Frontend framework | Next.js 15 (App Router) with React 19 |
| Database | PostgreSQL 16 |
| ORM | Prisma v6 |
| Architecture | Monorepo monolith (Turborepo + pnpm workspaces) |
| API pattern | REST API (versioned, `/api/v1/`) |
| Authentication | JWT with httpOnly cookies (access + refresh tokens) |
| Styling | Tailwind CSS v4 |
| State management | TanStack React Query v5 + React Context |
| Testing | Vitest (unit/integration) + Playwright (e2e) |
| Product search | PostgreSQL full-text search (tsvector/tsquery) |
| Image storage | AWS S3 with CloudFront CDN |
| Caching / rate limiting | Redis 7 |
| Email | Nodemailer + SMTP provider |
| Payment | Stripe (Payment Intents + webhooks) |
| CI/CD | GitHub Actions |
| Deployment | Docker Compose on VPS with Nginx reverse proxy |
| Performance target | Small scale (~100 concurrent users, <500ms API, <3s page load) |

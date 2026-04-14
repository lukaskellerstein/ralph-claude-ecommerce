# Ralph Claude Ecommerce

A full-stack ecommerce application built with **FastAPI** (Python) and **React** (TypeScript), designed and specified using the SpecKit workflow.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18+, TypeScript, Vite, shadcn/ui, Tailwind CSS, TanStack Query |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic |
| **Database** | PostgreSQL 16+ |
| **Payments** | Stripe Payment Intents API |
| **Auth** | JWT with httpOnly cookies, bcrypt |

## Feature Specifications

Each feature has a complete specification suite generated with SpecKit (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`):

| # | Feature | Description |
|---|---------|-------------|
| 001 | [Product Catalog](specs_backup/001-product-catalog/) | Categories, search, filtering, product detail, reviews |
| 002 | [Auth & User Management](specs_backup/002-auth-user-management/) | Registration, JWT auth, profile, addresses, password reset |
| 003 | [Shopping Cart & Checkout](specs_backup/003-shopping-cart-checkout/) | Cart CRUD, guest cart merge, multi-step checkout, Stripe payments |
| 004 | [Order Management](specs_backup/004-order-management/) | Order history, detail, cancellation/refund, wishlist, account dashboard |
| 005 | [Admin Dashboard](specs_backup/005-admin-dashboard/) | Product CRUD, category management, order processing, analytics, user management |

Each spec directory contains:

```
specs_backup/NNN-feature-name/
├── spec.md             # User stories, acceptance criteria, requirements
├── plan.md             # Technical context, architecture, project structure
├── research.md         # Design decisions with rationale
├── data-model.md       # Entity definitions, state transitions, validation
├── contracts/          # API endpoint contracts (request/response schemas)
├── quickstart.md       # Setup guide, dependencies, test instructions
├── tasks.md            # Implementation tasks organized by user story
└── checklists/         # Specification quality validation
```

## Getting Started with Specs

You have two options:

**Option A: Use the pre-generated specs**

```bash
mv specs_backup specs
```

**Option B: Regenerate specs from scratch**

```bash
# For each feature:
/speckit-specify ./docs/SPEC-001-PRODUCT-CATALOG.md
/speckit-plan
/speckit-tasks
```

## Project Structure

```
docs/                   # Raw feature requirement documents
specs_backup/           # Pre-generated specification suites (rename to specs/ to use)
.specify/               # SpecKit configuration, templates, and scripts
```
# ralph-claude-ecommerce Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-14

## Active Technologies
- Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, passlib[bcrypt], python-jose[cryptography], slowapi (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod (frontend) (000-specifications)
- PostgreSQL 16+ (000-specifications)
- Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod, @stripe/stripe-js, @stripe/react-stripe-js (frontend) (000-specifications)
- PostgreSQL 16+ with row-level locking (SELECT FOR UPDATE) for stock management (000-specifications)
- Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod (frontend) (000-specifications)
- Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe, python-multipart, cachetools (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod, recharts, react-md-editor (frontend) (000-specifications)
- PostgreSQL 16+, local filesystem for product images (000-specifications)

- Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod (frontend) (000-specifications)

## Project Structure

```text
src/
tests/
```

## Commands

cd src && pytest && ruff check .

## Code Style

Python 3.12+ (backend), TypeScript 5.x (frontend): Follow standard conventions

## Recent Changes
- 000-specifications: Added Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe, python-multipart, cachetools (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod, recharts, react-md-editor (frontend)
- 000-specifications: Added Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod (frontend)
- 000-specifications: Added Python 3.12+ (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, stripe (backend); React 18+, Vite, shadcn/ui, Tailwind CSS, TanStack Query, zod, @stripe/stripe-js, @stripe/react-stripe-js (frontend)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

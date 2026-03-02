# FastAPI Monolith Template

Production-grade FastAPI monolith with PostgreSQL, Redis, structured logging, Prometheus metrics, and full CI/CD.

## Features

- **FastAPI** with async SQLAlchemy 2.0, Pydantic v2, and automatic OpenAPI docs.
- **PostgreSQL** via asyncpg with Alembic migrations.
- **Redis** for caching (async client with hiredis).
- **Structured logging** via structlog (JSON in production, console in dev).
- **Prometheus metrics** at `/metrics`.
- **Health checks** at `/health`, `/health/live`, `/health/ready`.
- **Security headers** (CSP, HSTS, X-Content-Type-Options, X-Frame-Options).
- **Rate limiting** via slowapi.
- **Global exception handling** with consistent error shape.
- **Request ID propagation** (X-Request-ID header, bound to all logs).
- **Docker** multi-stage build, non-root user, tini for signal handling.
- **CI** with lint, type check, format check, test, coverage.
- **Security scanning** with Trivy and pip-audit.
- **Pre-commit hooks** with ruff, mypy, and commitizen.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Docker and Docker Compose
- PostgreSQL 17+
- Redis

## Quick Start

```bash
# Clone
npx degit teo-garcia/fastapi-template-monolith my-api
cd my-api

# Environment
cp .env.example .env
cp .env.test.example .env.test

# Start infrastructure
docker compose up -d db redis

# Install dependencies
uv sync

# Run migrations
make db-deploy

# Start dev server
make dev
```

The API is available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

## Scripts

| Command                             | Description                                        |
| ----------------------------------- | -------------------------------------------------- |
| `make dev`                          | Start dev server with hot reload                   |
| `make start`                        | Start production server (gunicorn)                 |
| `make build`                        | Build production Docker image                      |
| `make lint`                         | Lint and auto-fix with ruff                        |
| `make lint-check`                   | Lint check (CI mode, no fix)                       |
| `make lint-types`                   | Type check with mypy                               |
| `make format`                       | Format with ruff                                   |
| `make format-check`                 | Format check (CI mode)                             |
| `make test`                         | Run tests                                          |
| `make test-cov`                     | Run tests with coverage                            |
| `make test-e2e`                     | Run e2e tests only                                 |
| `make check`                        | Full check pipeline (lint + format + types + test) |
| `make db-migrate msg="description"` | Create new migration                               |
| `make db-deploy`                    | Apply migrations                                   |
| `make db-reset`                     | Reset database (down + up)                         |
| `make db-seed`                      | Seed development data                              |
| `make docker-dev`                   | Full stack via Docker Compose                      |

## Testing

Tests use pytest with pytest-asyncio. The test client uses httpx with ASGI transport (no real HTTP, no server needed).

```bash
# All tests
make test

# With coverage
make test-cov

# Only e2e tests (require database)
make test-e2e
```

Test database is configured via `.env.test`. The test suite creates and drops tables automatically.

## Health and Metrics

| Endpoint            | Purpose                             |
| ------------------- | ----------------------------------- |
| `GET /health/live`  | Liveness probe (always 200)         |
| `GET /health/ready` | Readiness probe (checks DB + Redis) |
| `GET /health`       | Full health (soft failure on Redis) |
| `GET /metrics`      | Prometheus-compatible metrics       |

## Architecture

```
app/
  main.py                 # App factory, lifespan, middleware stack
  config/
    settings.py           # Pydantic BaseSettings (all env vars validated here)
  shared/
    database/             # SQLAlchemy async engine + session
    redis/                # Async Redis client
    logging/              # structlog configuration
    middleware/           # Request ID, security headers, logging
    exceptions/           # Global exception handlers
    health/               # Health check endpoints
    metrics/              # Prometheus metrics + middleware
  modules/
    tasks/                # Feature module
      models.py           # SQLAlchemy model
      schemas.py          # Pydantic request/response schemas
      service.py          # Business logic
      router.py           # API endpoints
```

Each feature module follows the same pattern: `models.py` (database), `schemas.py` (validation), `service.py` (logic), `router.py` (HTTP).

## Deployment

```bash
# Build production image
docker build -f docker/Dockerfile -t my-api .

# Run with env vars
docker run -p 8000:8000 --env-file .env my-api
```

The production image uses gunicorn with uvicorn workers, runs as non-root, and includes tini for proper signal forwarding.

## Environment Variables

See `.env.example` for all available configuration. All variables are validated at startup via Pydantic BaseSettings. Missing required values cause immediate failure with a clear error message.

## Tooling Comparison (NestJS Parity)

| NestJS             | FastAPI                   | Role               |
| ------------------ | ------------------------- | ------------------ |
| pnpm               | uv                        | Package manager    |
| ESLint + Prettier  | ruff                      | Lint + format      |
| tsc --noEmit       | mypy --strict             | Type checking      |
| Jest               | pytest                    | Testing            |
| Supertest          | httpx (ASGI)              | E2E HTTP client    |
| Prisma             | SQLAlchemy + Alembic      | ORM + migrations   |
| class-validator    | Pydantic v2               | Validation         |
| @nestjs/config     | Pydantic BaseSettings     | Configuration      |
| @nestjs/swagger    | Built-in (automatic)      | API docs           |
| helmet             | SecurityHeadersMiddleware | Security headers   |
| @nestjs/throttler  | slowapi                   | Rate limiting      |
| Winston            | structlog                 | Structured logging |
| prom-client        | prometheus-client         | Metrics            |
| Husky + commitlint | pre-commit + commitizen   | Git hooks          |

## Related Templates

- [nest-template-monolith](https://github.com/teo-garcia/nest-template-monolith) - NestJS equivalent
- [nest-template-microservice](https://github.com/teo-garcia/nest-template-microservice) - NestJS microservice
- [react-template-next](https://github.com/teo-garcia/react-template-next) - Next.js frontend
- [react-template-rr](https://github.com/teo-garcia/react-template-rr) - React Router frontend

## License

MIT

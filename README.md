<div align="center">

# FastAPI Template Monolith

**Production-grade FastAPI monolith with PostgreSQL, Redis, structured
logging, Prometheus metrics, and full CI/CD**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)](https://docs.astral.sh/uv/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D?logo=redis&logoColor=white)](https://redis.io)

Part of the [@teo-garcia/templates](https://github.com/teo-garcia/templates)
ecosystem

</div>

---

## Features

| Category          | Technologies / Direction                               |
| ----------------- | ------------------------------------------------------ |
| **Framework**     | FastAPI with async SQLAlchemy 2.0 and Pydantic v2      |
| **Database**      | PostgreSQL via asyncpg and Alembic migrations          |
| **Cache**         | Redis with async client support                        |
| **Observability** | Health checks, Prometheus metrics, structured logging  |
| **Security**      | Security headers, rate limiting, request ID propagation |
| **Testing**       | Pytest, pytest-asyncio, coverage, HTTPX ASGI transport |
| **Code Quality**  | Ruff, mypy, pre-commit, commitizen                     |
| **DevOps**        | Docker, CI, Trivy, pip-audit                           |

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Docker and Docker Compose
- PostgreSQL 17+
- Redis

---

## Quick Start

```bash
# 1. Clone the template
npx degit teo-garcia/fastapi-template-monolith my-api
cd my-api

# 2. Setup environment
cp .env.example .env
cp .env.test.example .env.test

# 3. Start infrastructure
docker compose up -d db redis

# 4. Install dependencies
uv sync

# 5. Run migrations
make db-deploy

# 6. Start development server
make dev
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI

Open [http://localhost:8000/health](http://localhost:8000/health) for health
status

Open [http://localhost:8000/metrics](http://localhost:8000/metrics) for
Prometheus metrics

---

## Available Scripts

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

---

## Testing

Tests use pytest with pytest-asyncio. The test client uses HTTPX with ASGI
transport, so most tests run without a real HTTP server.

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run e2e tests only
make test-e2e
```

**Test Coverage:**

- **Unit tests**: Business logic and service behavior
- **API tests**: Endpoint coverage via HTTPX ASGI transport
- **E2E tests**: Database-backed flows where needed

---

## Health & Observability

### Health Checks

- `GET /health/live` - Liveness probe (always 200)
- `GET /health/ready` - Readiness probe (checks DB + Redis)
- `GET /health` - Full health summary

### Metrics

- `GET /metrics` - Prometheus-compatible metrics endpoint

### Logging

- Structured logs via structlog
- Request ID propagation through middleware
- Consistent error handling and response shape

---

## Architecture Notes

### Service Model

- Single-service REST API with broad module ownership
- Direct in-process module calls
- Redis is used for cache and readiness checks, not service messaging

### Project Structure

```text
app/
  main.py                 # App factory, lifespan, middleware stack
  config/
    settings.py           # Pydantic Settings and env validation
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

Each feature module follows the same pattern:
`models.py`, `schemas.py`, `service.py`, `router.py`.

---

## Deployment

### Docker

```bash
# Build production image
docker build -f docker/Dockerfile -t my-api .

# Run with env vars
docker run -p 8000:8000 --env-file .env my-api
```

The production image uses gunicorn with uvicorn workers, runs as non-root, and
includes tini for proper signal forwarding.

## Environment Variables

See `.env.example` for the full list. All variables are validated at startup
via Pydantic Settings, and missing required values fail fast.

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `LOG_LEVEL` | Logging verbosity | `info` |
| `ENVIRONMENT` | Runtime environment | `development` |

---

## Tooling Comparison (NestJS Parity)

| NestJS             | FastAPI                   | Role               |
| ------------------ | ------------------------- | ------------------ |
| pnpm               | uv                        | Package manager    |
| ESLint + Prettier  | ruff                      | Lint + format      |
| tsc --noEmit       | mypy --strict             | Type checking      |
| Jest               | pytest                    | Testing            |
| Supertest          | HTTPX (ASGI)              | E2E HTTP client    |
| Prisma             | SQLAlchemy + Alembic      | ORM + migrations   |
| class-validator    | Pydantic v2               | Validation         |
| @nestjs/config     | Pydantic Settings         | Configuration      |
| @nestjs/swagger    | Built-in (automatic)      | API docs           |
| helmet             | Security headers middleware | Security headers |
| @nestjs/throttler  | slowapi                   | Rate limiting      |
| Winston            | structlog                 | Structured logging |
| prom-client        | prometheus-client         | Metrics            |
| Husky + commitlint | pre-commit + commitizen   | Git hooks          |

---

## Related Templates

- [nest-template-monolith](https://github.com/teo-garcia/nest-template-monolith) -
  NestJS equivalent
- [nest-template-microservice](https://github.com/teo-garcia/nest-template-microservice) -
  NestJS microservice
- [react-template-next](https://github.com/teo-garcia/react-template-next) -
  Next.js frontend
- [react-template-rr](https://github.com/teo-garcia/react-template-rr) - React
  Router frontend

---

## License

MIT

<div align="center">

# FastAPI Template Monolith

**Production-grade FastAPI monolith with PostgreSQL, Redis, structured logging,
Prometheus metrics, and full CI/CD**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)](https://docs.astral.sh/uv/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)

Part of the [@teo-garcia/templates](https://github.com/teo-garcia/templates)
ecosystem

</div>

---

## Features

| Category          | Technologies                                          |
| ----------------- | ----------------------------------------------------- |
| **Framework**     | FastAPI with async SQLAlchemy 2.0 and Pydantic v2     |
| **Database**      | PostgreSQL via asyncpg and Alembic migrations         |
| **Cache**         | Redis with async client support                       |
| **Observability** | Health checks, Prometheus metrics, structured logging |
| **Security**      | Security headers, rate limiting, request ID propagation |
| **Testing**       | Pytest, pytest-asyncio, HTTPX ASGI transport          |
| **Code Quality**  | Ruff, mypy, pre-commit, commitizen                    |
| **DevOps**        | Docker, CI, Trivy, pip-audit                          |

---

## Requirements

- Python 3.12+
- uv (package manager)
- Docker and Docker Compose
- PostgreSQL 17+
- Redis

---

## Quick Start

```bash
uv sync
cp .env.example .env
cp .env.test.example .env.test
docker compose up -d db redis
make db-deploy
make dev
```

The app starts on `http://localhost:8000` and the OpenAPI docs are available at
`/docs`.

---

## Scripts

| Command                             | Description                              |
| ----------------------------------- | ---------------------------------------- |
| `make dev`                          | Start dev server with hot reload         |
| `make start`                        | Start production server (gunicorn)       |
| `make build`                        | Build production Docker image            |
| `make test`                         | Run tests                                |
| `make test-cov`                     | Run tests with coverage                  |
| `make check`                        | Full pipeline (lint + format + types + test) |
| `make lint`                         | Lint and auto-fix with ruff              |
| `make format`                       | Format with ruff                         |
| `make lint-types`                   | Type check with mypy                     |
| `make db-migrate msg="description"` | Create new migration                     |
| `make db-deploy`                    | Apply migrations                         |
| `make db-reset`                     | Reset database                           |

---

## Health and Observability

| Endpoint           | Description                        |
| ------------------ | ---------------------------------- |
| `GET /health/live` | Liveness probe (always 200)        |
| `GET /health/ready`| Readiness probe (checks DB + Redis)|
| `GET /health`      | Full health summary                |
| `GET /metrics`     | Prometheus-compatible metrics      |

Structured logs via structlog with request ID propagation.

---

## Environment Variables

| Variable       | Description                  | Default       |
| -------------- | ---------------------------- | ------------- |
| `DATABASE_URL` | PostgreSQL connection string | Required      |
| `REDIS_URL`    | Redis connection string      | Required      |
| `LOG_LEVEL`    | Logging verbosity            | `info`        |
| `ENVIRONMENT`  | Runtime environment          | `development` |

See `.env.example` for the full list.

---

## Project Structure

| Path                 | Purpose                                                          |
| -------------------- | ---------------------------------------------------------------- |
| `app/modules/tasks/` | Sample tasks domain with router, schemas, and service            |
| `app/shared/`        | Shared database, Redis, health, metrics, middleware, and logging |
| `app/main.py`        | FastAPI application bootstrap                                    |
| `alembic/`           | Database migrations                                              |
| `tests/`             | Pytest suite                                                     |
| `docker/`            | Development and production container files                       |

---

## Shared Governance

| Area               | Tooling                                             |
| ------------------ | --------------------------------------------------- |
| Dependency updates | Renovate                                            |
| Issue intake       | GitHub issue templates                              |
| Change review      | Pull request template                               |
| CI                 | GitHub Actions for lint, format, typecheck, and test |
| Security           | Trivy, dependency review, and `pip-audit`           |

---

## Tooling Comparison (NestJS Parity)

| NestJS             | FastAPI                   | Role               |
| ------------------ | ------------------------- | ------------------ |
| pnpm               | uv                        | Package manager    |
| ESLint + Prettier  | ruff                      | Lint + format      |
| tsc --noEmit       | mypy --strict             | Type checking      |
| Jest               | pytest                    | Testing            |
| Prisma             | SQLAlchemy + Alembic      | ORM + migrations   |
| class-validator    | Pydantic v2               | Validation         |
| Winston            | structlog                 | Structured logging |
| prom-client        | prometheus-client         | Metrics            |

---

## Related Templates

| Template                       | Description                |
| ------------------------------ | -------------------------- |
| `nest-template-monolith`       | NestJS equivalent          |
| `fastapi-template-microservice` | FastAPI microservice      |
| `react-template-next`          | Next.js frontend           |
| `react-template-rr`            | React Router frontend      |

---

## License

MIT

---

<div align="center">
  <sub>Built by <a href="https://github.com/teo-garcia">teo-garcia</a></sub>
</div>

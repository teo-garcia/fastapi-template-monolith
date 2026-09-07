#!/usr/bin/env bash

set -euo pipefail

image=${1:?container image is required}
network=production-smoke

# Invoked by the EXIT trap.
# shellcheck disable=SC2329
cleanup() {
  docker rm --force production-app production-db production-redis 2>/dev/null || true
  docker network rm "$network" 2>/dev/null || true
}

trap cleanup EXIT

docker network create "$network"
docker run --detach --name production-db \
  --network "$network" \
  --env POSTGRES_USER=postgres \
  --env POSTGRES_PASSWORD=postgres \
  --env POSTGRES_DB=fastapi_monolith \
  --health-cmd pg_isready \
  --health-interval 1s \
  --health-retries 30 \
  postgres:18-alpine
docker run --detach --name production-redis \
  --network "$network" \
  --health-cmd "redis-cli ping" \
  --health-interval 1s \
  --health-retries 30 \
  redis:alpine

for _ in $(seq 1 30); do
  database=$(docker inspect --format '{{.State.Health.Status}}' production-db)
  redis=$(docker inspect --format '{{.State.Health.Status}}' production-redis)
  if [[ $database == healthy && $redis == healthy ]]; then
    break
  fi
  sleep 1
done

if [[ $(docker inspect --format '{{.State.Health.Status}}' production-db) != healthy ]] ||
  [[ $(docker inspect --format '{{.State.Health.Status}}' production-redis) != healthy ]]; then
  docker logs production-db
  docker logs production-redis
  exit 1
fi

docker run --detach --name production-app \
  --network "$network" \
  --publish 127.0.0.1:43118:8000 \
  --env DATABASE_URL=postgresql+asyncpg://postgres:postgres@production-db:5432/fastapi_monolith \
  --env REDIS_HOST=production-redis \
  --env OTEL_ENABLED=false \
  "$image"

for _ in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:43118/health/live >/dev/null; then
    exit 0
  fi
  sleep 1
done

docker logs production-app
exit 1

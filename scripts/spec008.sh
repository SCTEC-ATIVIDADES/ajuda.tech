#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  printf '%s\n' "Uso: $0 [up|health|normal|duplicate|invalid|signature|all|logs|down]"
}

compose_up() {
  docker compose up -d --build
}

webhook() {
  python3 scripts/spec008_webhook.py "$@"
}

health() {
  local retries="${HEALTH_RETRIES:-30}"
  local delay="${HEALTH_DELAY:-2}"
  local attempt
  for ((attempt = 1; attempt <= retries; attempt++)); do
    if curl --silent --show-error --fail-with-body "${N8N_HEALTH_URL:-http://localhost:5678/healthz}" >/dev/null && \
      curl --silent --show-error --fail-with-body "${APP_HEALTH_URL:-http://localhost:8001/}" >/dev/null; then
      printf '%s\n' 'ok'
      return 0
    fi
    sleep "$delay"
  done
  printf '%s\n' 'serviços não ficaram prontos' >&2
  return 1
}

normal() {
  webhook --target n8n normal
}

duplicate() {
  webhook --target n8n duplicate
}

invalid() {
  webhook --target app invalid
}

signature() {
  webhook --target app signature
}

logs() {
  docker compose logs --no-color --tail="${LOG_LINES:-100}" app n8n
}

down() {
  docker compose down
}

case "${1:-}" in
  up) compose_up ;;
  health) health ;;
  normal) normal ;;
  duplicate) duplicate ;;
  invalid) invalid ;;
  signature) signature ;;
  all) compose_up; health; normal; duplicate; invalid; signature; logs ;;
  logs) logs ;;
  down) down ;;
  *) usage; exit 2 ;;
esac

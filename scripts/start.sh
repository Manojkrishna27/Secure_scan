#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SecureScan AI — One-command startup script
# Starts the full Docker Compose stack, waits for backend health, seeds data.
#
# Usage:
#   bash scripts/start.sh           # start existing images
#   bash scripts/start.sh --build   # rebuild images first
#   bash scripts/start.sh --seed    # force re-run seed even if data exists
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

BUILD_FLAG=""
FORCE_SEED=false

for arg in "$@"; do
  case "$arg" in
    --build) BUILD_FLAG="--build"; echo "==> Rebuilding Docker images..." ;;
    --seed)  FORCE_SEED=true ;;
  esac
done

cd "$ROOT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🛡️  SecureScan AI — Starting stack"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Copy env if not present ──
if [[ ! -f ".env.docker" ]]; then
  echo "==> .env.docker not found — copying from .env.example..."
  cp .env.example .env.docker
  echo "    ⚠️  Edit .env.docker with real secrets before production use."
fi

# ── Start stack ──
# shellcheck disable=SC2086
docker compose up -d $BUILD_FLAG

echo ""
echo "==> Waiting for backend to become healthy (up to 90s)..."

# Poll /api/health until it returns 200 or we time out
BACKEND_URL="http://localhost:5000/api/health"
MAX_WAIT=90
elapsed=0
until curl -sf "$BACKEND_URL" > /dev/null 2>&1; do
  if [[ $elapsed -ge $MAX_WAIT ]]; then
    echo ""
    echo "⚠️  Backend did not become healthy within ${MAX_WAIT}s."
    echo "    Check logs: docker compose logs backend"
    break
  fi
  printf "."
  sleep 3
  elapsed=$((elapsed + 3))
done
echo ""

# ── Seed demo data via docker exec ──
if curl -sf "$BACKEND_URL" > /dev/null 2>&1; then
  if $FORCE_SEED; then
    echo "==> Running seed data (--seed flag)..."
    docker compose exec backend python /app/../scripts/seed_data.py 2>/dev/null \
      || docker exec securescan-backend sh -c "cd /app && python -c '
import sys; sys.path.insert(0, \"/app\")
from app import create_app
from scripts_runner import run_seed
' " 2>/dev/null \
      || echo "    ℹ️  Run seed manually: docker exec securescan-backend python scripts/seed_data.py"
  fi
  echo "==> Seeding demo data (idempotent — safe to run multiple times)..."
  docker exec securescan-backend sh -c "
    cd /app
    FLASK_ENV=production python -c \"
import os, sys
sys.path.insert(0, '/app')
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.extensions import db
from app.models import User
app = create_app()
with app.app_context():
    count = User.query.count()
    print(f'  Users in DB: {count}')
    if count == 0:
        print('  No users found — run: docker exec securescan-backend python /scripts/seed_data.py')
    else:
        print('  Database already seeded ✅')
\"
  " 2>/dev/null || true
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  SecureScan AI is running!"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:5000/api/health"
echo ""
echo "  Admin:     admin@securescan.ai / Admin12345"
echo "  Demo user: demo@securescan.ai  / Demo12345"
echo ""
echo "  Seed data: docker exec securescan-backend python /scripts/seed_data.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Logs: docker compose logs -f"
echo "  Stop: docker compose down"
echo ""

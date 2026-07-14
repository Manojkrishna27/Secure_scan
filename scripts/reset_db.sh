#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SecureScan AI — Hard-reset the local development database
# Drops the database, recreates it, runs all migrations, seeds demo data.
#
# ⚠️  DESTRUCTIVE — all existing data will be lost.
#
# Usage:  bash scripts/reset_db.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/backend"

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${CYAN}==>${NC} $1"; }
ok()   { echo -e "${GREEN}✅${NC}  $1"; }
warn() { echo -e "${YELLOW}⚠️${NC}   $1"; }
die()  { echo -e "${RED}❌${NC}  $1" >&2; exit 1; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔄  SecureScan AI — DB Reset"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
warn "This will DESTROY all data in the local database."
read -r -p "Are you sure? (y/N): " confirm
[[ "${confirm,,}" == "y" ]] || { echo "Aborted."; exit 0; }

# ── Activate virtual environment (if present) ──
if [[ -f "$BACKEND_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/.venv/bin/activate"
  ok "Activated .venv"
elif [[ -f "$BACKEND_DIR/venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/venv/bin/activate"
  ok "Activated venv"
else
  warn "No virtual environment found — using system Python."
fi

# ── Load env vars ──
if [[ -f "$BACKEND_DIR/.env" ]]; then
  # Export each line that isn't a comment or blank
  set -o allexport
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/.env"
  set +o allexport
  ok "Loaded backend/.env"
else
  die "backend/.env not found. Run: cp backend/.env.example backend/.env and fill in credentials."
fi

# ── Resolve MySQL connection params ──
DB_HOST="${MYSQL_HOST:-localhost}"
DB_PORT="${MYSQL_PORT:-3306}"
DB_USER="${MYSQL_USER:-securescan}"
DB_PASS="${MYSQL_PASSWORD:-}"
DB_NAME="${MYSQL_DB:-${MYSQL_DATABASE:-securescan}}"
ROOT_PASS="${MYSQL_ROOT_PASSWORD:-}"

# Prefer root password for DROP/CREATE (needs elevated perms)
if [[ -n "$ROOT_PASS" ]]; then
  ADMIN_USER="root"
  ADMIN_PASS="$ROOT_PASS"
else
  warn "MYSQL_ROOT_PASSWORD not set — using MYSQL_USER for DROP/CREATE (may fail)."
  ADMIN_USER="$DB_USER"
  ADMIN_PASS="$DB_PASS"
fi

# ── Drop and recreate database ──
log "Dropping database '$DB_NAME'..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$ADMIN_USER" -p"$ADMIN_PASS" \
  -e "DROP DATABASE IF EXISTS \`${DB_NAME}\`;" 2>/dev/null \
  || die "Failed to drop database. Check your MySQL credentials."

log "Creating database '$DB_NAME'..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$ADMIN_USER" -p"$ADMIN_PASS" \
  -e "CREATE DATABASE \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" \
  || die "Failed to create database."

# Ensure DB user has privileges (idempotent)
if [[ "$ADMIN_USER" == "root" ]]; then
  mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p"$ROOT_PASS" \
    -e "GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'%'; FLUSH PRIVILEGES;" \
    2>/dev/null || warn "Could not grant privileges — skipping (might already be set)."
fi
ok "Database recreated"

# ── Run Alembic migrations ──
log "Running Flask DB migrations..."
export FLASK_APP=app:create_app
cd "$BACKEND_DIR"
flask db upgrade
ok "Migrations applied"

# ── Seed data ──
log "Seeding admin user..."
python "$SCRIPT_DIR/seed_admin.py"

log "Seeding demo data..."
python "$SCRIPT_DIR/seed_data.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ok "Database reset complete!"
echo ""
echo "  Login: admin@securescan.ai / Admin12345"
echo "  Demo:  demo@securescan.ai  / Demo12345"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

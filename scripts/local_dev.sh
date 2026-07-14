#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SecureScan AI — Local development setup (no Docker)
# Sets up virtualenv, installs deps, runs DB init, starts both servers
# Usage:  bash scripts/local_dev.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# ── Colors ──
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${CYAN}==>${NC} $1"; }
ok()  { echo -e "${GREEN}✅${NC} $1"; }
warn(){ echo -e "${YELLOW}⚠️${NC}  $1"; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🛡️  SecureScan AI — Local Dev Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Python virtualenv ──
log "Setting up Python virtual environment..."
if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
  python3 -m venv "$BACKEND_DIR/.venv"
  ok "Created .venv"
else
  ok ".venv already exists"
fi

# shellcheck disable=SC1091
source "$BACKEND_DIR/.venv/bin/activate"

log "Installing Python dependencies..."
pip install -q -r "$BACKEND_DIR/requirements.txt"
ok "Python deps installed"

# ── .env ──
if [[ ! -f "$BACKEND_DIR/.env" ]]; then
  warn "backend/.env not found — copying from backend/.env.example"
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  warn "Edit backend/.env with your MySQL credentials before proceeding."
  exit 1
fi

# ── DB migrations ──
log "Running database migrations..."
export FLASK_APP=app:create_app
cd "$BACKEND_DIR"
flask db upgrade
ok "Migrations applied"

# ── Seed data ──
log "Seeding demo data..."
python "$SCRIPT_DIR/seed_admin.py"
python "$SCRIPT_DIR/seed_data.py"
ok "Seed data loaded"

# ── Node deps ──
log "Installing Node.js dependencies..."
cd "$FRONTEND_DIR"
npm install --silent
ok "Node deps installed"

# ── Start servers ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Starting servers..."
echo ""
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:5000/api/health"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start backend in background
cd "$BACKEND_DIR"
FLASK_ENV=development FLASK_DEBUG=1 python app.py &
BACKEND_PID=$!

# Start frontend
cd "$FRONTEND_DIR"
VITE_API_BASE_URL=http://localhost:5000 npm run dev &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '👋  Servers stopped.'" EXIT INT TERM

wait

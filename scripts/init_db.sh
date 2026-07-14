#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SecureScan AI — Database initialisation
# Runs flask db upgrade + seeds admin user + seeds demo data
# Usage:  bash scripts/init_db.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/backend"

echo "==> Activating virtual environment (if exists)..."
if [[ -f "$BACKEND_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/.venv/bin/activate"
elif [[ -f "$BACKEND_DIR/venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/venv/bin/activate"
fi

export FLASK_APP=app:create_app

cd "$BACKEND_DIR"

echo ""
echo "==> Running Flask DB migrations..."
flask db upgrade

echo ""
echo "==> Seeding admin user..."
python "$SCRIPT_DIR/seed_admin.py"

echo ""
echo "==> Seeding demo data..."
python "$SCRIPT_DIR/seed_data.py"

echo ""
echo "✅ Database initialised successfully."
echo "   Login: admin@securescan.ai / Admin12345"
echo "   Demo:  demo@securescan.ai  / Demo12345"

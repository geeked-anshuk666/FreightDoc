#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== backend deterministic tests =="
(cd "$ROOT_DIR/backend" && python -m pytest tests -m "not live" -q)

echo "== frontend build checks =="
(cd "$ROOT_DIR/frontend" && npm ci && npm test -- --run && npm run build)

echo "== release/security checks =="
python "$ROOT_DIR/scripts/verify_release.py"

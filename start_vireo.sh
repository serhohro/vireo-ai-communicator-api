#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo ""
echo "  ================================================================"
echo "    Vireo v3.1 - Interoperability Release"
echo "  ================================================================"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "  [ERROR] python3 not found"
    exit 1
fi

if ! python3 -c "import flask, nacl, z3" >/dev/null 2>&1; then
    echo "  [INFO] Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "  [INFO] Starting Vireo on http://localhost:5000"
exec python3 -m api.server

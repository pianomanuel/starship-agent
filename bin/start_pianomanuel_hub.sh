#!/bin/bash
# Pianomanuel hub: HTTP :8080 (redirects HTML to HTTPS) + HTTPS :8444. Restored 2026-09-26.
# Stable paths only (no /Volumes names, nothing written to MainDB).
set -euo pipefail
H="$HOME/ManuelOps/hub"
export TMPDIR="$H/tmp" PYTHONUNBUFFERED=1
export HUB_ROOT="$H/root" HUB_CERT="$H/certs/main_thing.crt" HUB_KEY="$H/certs/main_thing.key" HUB_SEC_DB="$H/secure/security.db"
cd "$H/server"
exec /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 "$H/server/hub_server.py"

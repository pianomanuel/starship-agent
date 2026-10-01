#!/bin/bash
# Main Thing HTTPS API on 127.0.0.1:8443. Restored 2026-09-26.
# MAINDB points at ~/ManuelOps/hub/mainthing/data (copy of main_thing.db from 2026-09-19), never ~/Documents/MainDB.
set -euo pipefail
H="$HOME/ManuelOps/hub"
export TMPDIR="$H/tmp" PYTHONUNBUFFERED=1 MAINDB="$H/mainthing/data"
TOKEN="$MAINDB/.main_thing_token"
if [[ ! -f "$TOKEN" ]]; then
  ( umask 077; /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -c 'import secrets; print(secrets.token_urlsafe(32), end="")' > "$TOKEN" )
fi
cd "$H/mainthing"
exec /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m uvicorn main_thing_api:app \
  --host 127.0.0.1 --port 8443 --ssl-keyfile "$H/certs/main_thing.key" --ssl-certfile "$H/certs/main_thing.crt"

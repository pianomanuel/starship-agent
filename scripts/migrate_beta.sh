#!/bin/sh
# migrate_beta.sh — apply schema/NNN_*.sql to ManuelOps_BETA.sqlite only
# Skip *.mssql.sql. Never touch ManuelOps.sqlite.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
DB="${MANUELOPS_BETA_DB:-$ROOT/data/ManuelOps_BETA.sqlite}"
SCHEMA="${MANUELOPS_SCHEMA:-$ROOT/schema}"
case "$DB" in *ManuelOps.sqlite) echo "refused: prod sqlite"; exit 2;; esac
command -v sqlite3 >/dev/null || { echo "need sqlite3"; exit 1; }
mkdir -p "$(dirname "$DB")"
sqlite3 "$DB" "PRAGMA foreign_keys=ON;"
cur=$(sqlite3 "$DB" "PRAGMA user_version;")
[ "$(sqlite3 "$DB" "SELECT count(*) FROM sqlite_master WHERE name='meta';")" = "0" ] && cur=-1
for f in "$SCHEMA"/[0-9][0-9][0-9]_*.sql; do
  [ -f "$f" ] || continue
  case "$f" in *.mssql.sql) continue ;; esac
  base=$(basename "$f"); ver=${base%%_*}; ver=$((10#$ver))
  [ "$ver" -gt "$cur" ] || continue
  echo "apply $base ($cur -> $ver)"
  sqlite3 "$DB" <<SQL
PRAGMA foreign_keys=ON;
$(cat "$f")
PRAGMA user_version=$ver;
INSERT INTO change_log(action,approved_by,detail)
  VALUES('migrate','migrate_beta.sh','applied $base');
INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version','$ver');
INSERT OR REPLACE INTO meta(key,value) VALUES('compile_date',date('now'));
INSERT OR REPLACE INTO meta(key,value) VALUES('beta_flag','BETA');
SQL
  cur=$ver
done
echo "done user_version=$cur db=$DB"

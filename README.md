# ManuelOps

Private **primary database** for J. Robert Manuel (Life Resume / Circles of Joy).

## What lives here

- `schema/000_schema.sql` — CREATE TABLE only
- `schema/ManuelOps.sql` — full seed dump (no High-sensitivity rows)
- `LOCK.md` — approval rule

## What this replaced

- `pianomanuel/SQL` public seed dump (leave as archive)
- Duplicate Google Drive sheets named `ManuelOps_Seed_Database_2026-09-11` and `ManuelOps_Music_Library_Database_2026-09-11` (older copies sent to Trash)
- Project files `ManuelOps_Seed.sqlite` / `.sql` / seed workbooks

Working copy also sits in the Grok project as `ManuelOps.sqlite`.

## Load

```bash
sqlite3 ManuelOps.sqlite < schema/000_schema.sql
sqlite3 ManuelOps.sqlite < schema/ManuelOps.sql
```

Do not commit clinical packets, SS amounts, passwords, or the Jim letter body.

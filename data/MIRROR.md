# Mirrors retired — 2026-09-14

Owner sign-off: delete the *index of twins*, not the staff workbooks.

## Source of truth
- Code + compiled `site/`: private GitHub `pianomanuel/ManuelOps` on `main`.
- Workbooks: Google Drive folder ManuelOps (ops only). One copy per workbook. Do not mint a second MASTER.
- Local `~/Sites/pianomanuel_new_build` and `/mnt/data` pastes are **not** truth. Do not copy the build back onto local drives.

## What this file no longer does
- No candidate-MASTER pair.
- No test-folder / parent-mirror-test as live pointers.
- No instruction to treat a local Hub or `pianomanuel.com:8080` as published HTTPS.

## Still Drive-only (do not commit bodies)
- Health / Living workbook
- Clinical packets, SS amounts, Fun-vault, Jim letter

## Load (unchanged)
```bash
sqlite3 ManuelOps_BETA.sqlite < schema/000_schema.sql
sqlite3 ManuelOps_BETA.sqlite < schema/001_circles.sql
```
Do not overwrite `ManuelOps.sqlite` until a later sign-off names that file.

GitHub issue for this cut: see #25 plus the 2026-09-14 finalize comment.

# ManuelOps — Copilot instructions

Private ops repo for J. Robert Manuel / pianomanuel. Not a public site.

## Roofs
- Code + compiled `site/`: this repo on `main`.
- Workbooks: Google Drive folder ManuelOps. One copy per workbook.
- Jira PCS is login-only. Do not invent Jira writes.
- OneDrive is not connected.

## Hard lock
- Do not put clinical notes, passwords, tokens, Fun-vault paths, or Jim letter body in HTML, SQL, or commits.
- Do not enable public DNS or GitHub Pages unless Robert says so.
- Do not overwrite `ManuelOps.sqlite`. Load only `data/ManuelOps_BETA.sqlite`.
- Do not send the Roppa letter. Do not put TRK-007 on a calendar.
- Do not invent Gemini or Meta product sync.
- Skip `schema/*.mssql.sql` unless the task is explicitly MSSQL schema-only.

## Schema
- Numbered files: `schema/000_schema.sql`, `001_circles.sql`, `011_meta.sql`.
- Runner: `scripts/migrate_beta.sh` (refuses prod sqlite).
- New schema = new `NNN_name.sql`. Do not rewrite a shipped file.
- Drafts `020` / `022` stay off `main` until Robert approves.

## Site
- Home is `site/index.html` (Window). Board is `site/board.html`.
- `public_dns=off`. Meta keys live in `schema/011_meta.sql` and `site/meta.html`.

## How to work
- Prefer ADD/EXTEND over delete.
- Smallest change that exits 0/1.
- After schema work, say how to run `./scripts/migrate_beta.sh` and `PRAGMA user_version`.

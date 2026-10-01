---
applyTo: "schema/**"
---

Schema lane only.

- New work is a new numbered `NNN_name.sql`. Do not rewrite a shipped file.
- Drafts `020` and `022` stay off `main` until Robert approves.
- Skip `*.mssql.sql` unless the task is explicitly MSSQL schema-only.
- Do not overwrite `ManuelOps.sqlite`. Load only `data/ManuelOps_BETA.sqlite`.
- After edits, tell the operator to run `./scripts/migrate_beta.sh` and `PRAGMA user_version`.
- No clinical notes, passwords, tokens, Fun-vault paths, or Jim letter body in SQL.

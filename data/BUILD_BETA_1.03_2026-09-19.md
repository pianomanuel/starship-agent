# BUILD — BETA 1.03 — 2026-09-19

Version label: **BETA 1.03** (staff compile). Not a DNS cutover. Not prod sqlite.

## Approver
Joseph Robert Manuel, IV / @pianomanuel. LOCK: major changes need this sign-off.
There is no second Jira roof and no auto-merge.

## What this build is
| Key | Value |
|---|---|
| schema_version / user_version | 12 |
| compile_date | 2026-09-19 |
| beta_flag | BETA |
| public_dns | off |
| engine | sqlite (MSSQL schema_only) |
| source_of_truth | github site+schema; Drive workbooks; sqlite=BETA only |
| Window | Mental Canvas `p3cpw7wsusj` + Meta rail |

## Already on main (this PR adds the packet only)
- `scripts/migrate_beta.sh` — refuses `ManuelOps.sqlite`
- `schema/012_meta_sync.sql` — workaround; do not rewrite 011
- `schema/011_meta.sql` + `.mssql.sql` — meta keys
- `site/meta.html` — snapshot v12
- `site/index.html` — Meta Muse rail
- `.github/copilot-instructions.md`

## Not in this build
- `ManuelOps.sqlite` overwrite
- GitHub Pages / public DNS
- Clinical notes, passwords, Fun-vault, Jim body
- Roppa send / TRK-007 calendar
- In-scene GitHub blob links (private repo 404 to strangers)
- Draft schema 020 / 022

## How to verify after pull
```
git checkout main && git pull origin main
chmod +x scripts/migrate_beta.sh && ./scripts/migrate_beta.sh
sqlite3 data/ManuelOps_BETA.sqlite "PRAGMA user_version;"
```
Expect `12`.

## Approval checkbox (human)
- [ ] Keep BETA 1.03 label
- [ ] Meta Muse rail is acceptable
- [ ] Do not promote MSSQL
- [ ] Do not turn DNS on

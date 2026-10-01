# Security checks — finalize 2026-09-14

Source of policy: LOCK.md + security/E2E.md + issues #9 #10.
Ordinary site security is headers + robots + no secrets in HTML.
This is not a new crypto product.

## Pass
- Repo `pianomanuel/ManuelOps` is private.
- LOCK.md is on `main`.
- Compiled `site/` HTML has no passwords, tokens, .p8, street address, or Jim body.
- Jira API still not connected (correct).
- Health workbook stays Drive-only.
- Mirror *index* retired in `data/MIRROR.md` and `site/MIRROR.md`.
- `site/robots.txt` disallows crawlers.
- `site/_headers` + landing CSP: nosniff, no-referrer, SAMEORIGIN, tight frame-src.
- Bookmarks no longer present `:8080` as a live link.
- Public DNS / GitHub Pages remain **off** (E2E.md).

## Fail / gap (named, not papered over)
- GitHub secret scanning: still disabled on this account class (API 404 historically).
- Branch ruleset on `main`: not applied on free private repo (#9).
- `jira-open-3d.html` still loads Three.js from unpkg if that page is opened — third-party JS.
- Local Mac `~/Sites` cannot be deleted from this side. Owner deletes that tree if it still exists.
- Drive twin sheets were *unlinked from the index*, not mass-trashed, so Health / Seed archives survive.

## Incident path (unchanged)
Assume leak = HTML or chat paste. Rotate Apple + GitHub + Google sessions. Restore from Drive version / quarantine / git. Do not make the repo public to buy a ruleset.

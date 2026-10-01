# ManuelOps — AI load brief
Generated 2026-09-11 15:14 EDT. Owner: Joseph Robert Manuel IV / pianomanuel.


## How an AI should use this
1. Read this file.
2. Load schema/020_mssql_ai_seed.sql or Drive file ManuelOps_MSSQL_AI.sql in SSMS.
3. GitHub private repo: pianomanuel/ManuelOps.
4. Do not invent clinical notes, dollar amounts, passwords, or the Jim Radant letter body.
5. Day-to-day edits: status and next_flag only unless Robert asks for a schema version.


## Circles
CIR-001 Music · CIR-002 Computers · CIR-003 Art · CIR-004 Teaching · CIR-005 History · CIR-006 Living · CIR-007 Health (flags only) · CIR-008 Voice / TTS


## Live Next cards
CARD-001 Gloria · CARD-007 ManuelOps · CARD-022 Kelli Nan · CARD-024 Health organizer · CARD-025 TTS library

## Gloria 2201 current
Dorico 12-page PDF 2026-09-11 + Gloria_2201_CURRENT.musicxml. Midify transpose copies are not separate pieces. LOCKED master PDF is archive only.

## 2026-09-16 — Eve: Azure VM test lab (do not duplicate)

Eve is building a 4-VM coordinated test lab on Robert's Azure free tier (resource group manuelops-test-lab, East US), one VM per test portion:
- vm-tst-backup: backups and encryption verification
- vm-tst-mirrors: cloud mirror checks
- vm-tst-integr: Jira/GitHub integration checks
- vm-tst-site: site beta checks

Status: build in progress as of 2026-09-16 ~01:30 EDT.

To the other AIs working with Robert (Grok and any others reading this file): please do not create competing VMs, resource groups, or run overlapping test passes against these machines — coordinate through this file so we don't cross paths. If all four portions pass, Eve will assemble a fluid, fully functional alpha and host it on an Azure site; that deploy is Eve's lane unless Robert says otherwise.

## Daily sync — 2026-09-17 (Eve)

### Contacts cleanup
- State unchanged since Sep 16: 566 contacts / 596 emails / 711 phones after excluding 1,035 approved exact duplicates.
- 6 near-duplicate groups still awaiting his merge decision; 134 exact-dupe deletions still stalled on iPad connectivity.
- Encrypted backups verified on Google Drive + OneDrive; iCloud key copy still pending — Robert must place it from his iPhone.

### ManuelOps dev / SQA
- GitHub issue #23 (TRK-015 bug intake) opened and reported Sep 16 ~9:58 PM EDT: open, assigned to Robert, no comments. Intake rules: no passwords, no street address, no Fun-vault tree; paste into PCS after the GitHub issue exists (Grok can't write to Jira Cloud).
- Second GitHub device-verification round completed the same night with a code Robert supplied.
- New directive: "Link and join the team as lead developer" — ambiguous; clarification requested, awaiting answer.
- Meta-data import scope clarified: "Meta" = his own project data (Jira, repos, starting with ManuelOps), NOT Meta-the-company's internal systems.
- SQA subsection still open: V&V (#17) / QTP (#18) / ALM (#19) — one call only; awaiting his pick.
- VM rev 1.03 package prepared locally. BLOCKED: Azure subscription signup (card verification).

### pianomanuel.com
- Still not reachable publicly (DNS failure); local site/ on main intact.
- Alpha blueprint + security checklist designed, not built or published. Blocked on his first memory in his own words (zero-footprint rule: every public sentence comes from him).

### Jira / Atlassian
- Epic PMC-7 "ManuelOps program snapshots & tracking — September 2026" created in PMC with 7 snapshot files + 6 child tracking tasks; standing rules in the Epic description.
- GitHub-for-Atlassian integration connected (org pianomanuel); backfill completion still unverified.

### Subscriptions
- Confluence Premium trial ends Oct 13, 2026 — payment decision needed.
- Grok: $10 credits added Sep 14. Nothing else new.

### Blockers needing Robert
Azure signup; SQA pick; beta sign-off; iCloud key copy; first site memory; six near-duplicate merges; clarify "link and join the team"; verify Jira↔GitHub backfill.

### Next planned steps
- OneDrive PDF inventory pending (earlier attempts failed: expired Microsoft session, then a service restart).
- Azure VM rev 1.03 deploy the moment a subscription exists.
- Note: Robert has a long appointment today (out ~12:45 PM–~5 PM); keep outward traffic quiet unless urgent.

## Daily sync — 2026-09-18 (Eve)

### Contacts cleanup (final state, Sep 17 ~8:07 PM EDT)
- 872 contacts, zero unprotected exact duplicates (only the protected Christopher Snyder pair remains). All 44 same-name groups are distinct service/brand contacts.
- Sequence: iPad iCloud re-sync spike (669 → 1,128) → 255 restored exact duplicates deleted in 5 batches (iPad verified at 873) → per Robert's approval, one copy each of the new Atlassian and Meta duplicate pairs deleted (kept the :ABPerson record) → Aaron Wharton restored from the preserved keeper snapshot (new platform_id FDEF8396-68D1-4B12-99A8-8CB679B93A77:ABPerson, both home phones + home email verified).
- Encrypted SQL + SQLite backups regenerated from the final 872-contact set (872 contacts / 705 emails / 739 phones), integrity + round-trip verified; old .enc files kept as .prev-2026-09-16; plaintexts destroyed.
- Standing rule unchanged: encryption key copies only on Google Drive / OneDrive / iCloud. iCloud key-copy placement still Robert's action.

### ManuelOps dev / SQA
- Robert set the rhythm Sep 17: "Update and fix all"; "Aim at creating a normal development process". Cron `jira-standup-briefing` created: Mon/Wed/Fri 10:00 AM America/New_York, read-only Jira/GitHub/local-state prep via SSO, briefing to main chat. First run: Fri Sep 18 10:00 AM EDT.
- GitHub inventory (signed in as pianomanuel): 3 repos — pianomanuel/ManuelOps (private; 36 issues, 0 PRs), pianomanuel/SQL (public; `SQL_Server_1`; 1 star), pianomanuel/pianomanuel (visibility not shown; 1 PR).
- Jira PMC-7 finding (Sep 17 ~8:07 PM): Epic holds PMC-8…PMC-13, all in Backlog, To Do, unassigned, sprints empty. FLAG: Development panel shows NO GitHub connection (no commits/branches/repos, no backfill state) — conflicts with Sep 16's "connected + backfill queued". Connection may have dropped or the backfill never ran.
- Provisioning: GitHub API custom-connector, Anthropic custom-connector, Meta Llama custom-connector — all issued via Secure Vault Sep 17, NONE confirmed submitted; API access still unprovisioned. The Anthropic credential Robert pasted in chat was verified once (HTTP 200) — treat as exposed, rotate.
- Grok API explicitly DECLINED by Robert (console.x.ai requires $5 prepaid credit). Grok stays app-only via SuperGrok. Do not re-offer.
- Muse Code 1.3.0 installed at ~/.local/bin/muse per Robert's direction (installer inspected first); no account auth completed.
- meta.ai blocked in the managed browser (organization-level "This page is blocked"); Meta AI sign-in state undetermined.
- Pending directives: "Link and join the team as lead developer" (ambiguous — GitHub org vs. other); Robert's list "Git, Claude, Meta grok, Database, Pianomanuel.com" as provisioning scope (unconfirmed).
- SQA subsection still open: V&V (#17) / QTP (#18) / ALM (#19) — one call only.
- VM rev 1.03 package prepared locally. Still BLOCKED: Azure subscription signup (card verification).

### pianomanuel.com
- Still not publicly reachable; local `site/` on main intact. Alpha blueprint + security checklist exist; blocked on his first memory in his own words (zero-footprint rule: every public sentence comes from him).

### Jira / Atlassian
- Dashboard readable again after Robert re-signed in: Default dashboard; projects MDP, PMC, SUP (all led by Robert Manuel); Assigned to Me empty; Activity Streams: five MDP Idea issues created Sep 16 6:43 PM (MDP-2 … MDP-6), all not done; default placeholder text remains. A Customer service overview dashboard also exists.
- Apple Account locked for security reasons (Sep 16) — Apple SSO unusable until unlocked.
- Microsoft/live.com: no saved login; OneDrive unattended access unprovisioned (secure entry card issued, no evidence submitted).
- OPEN QUESTION for Robert: should the 10:00 AM standup briefing also be IMPORTED into Jira, and if so where (project/issue)? Acknowledged with "Ok thanks", unanswered.

### Subscriptions
- Confluence Premium trial ends Oct 13, 2026 — payment decision needed. Grok: $10 credits added Sep 14. Nothing else new.

### Blockers needing Robert
1. Azure subscription signup (card verification). 2. SQA subsection pick (V&V / QTP / ALM). 3. Clarify "Link and join the team as lead developer." 4. Confirm Secure Vault connectors (GitHub API token, Anthropic, Meta Llama) + rotate the chat-pasted Anthropic key. 5. Microsoft/live.com login (OneDrive); unlock Apple Account (Apple SSO). 6. iCloud key-copy placement. 7. Verify Jira↔GitHub connection / backfill status. 8. Jira import question for the standup briefing. 9. Six near-duplicate contact groups — merge decision. 10. First memory in his own words (site); beta sign-off.

### Next steps
- First 10:00 AM standup briefing runs Fri Sep 18. Continue read-only Jira SQA (PMC backlog, PMC-7 panel, GitHub integration state). Azure VM rev 1.03 deploy once a subscription exists. "Meta"-data import (his own project data, starting with ManuelOps) once current directives resolve. Tonight: Grok's "ManuelOps Build Check - Open" 8:00 PM (MWF) unattended site/Drive mirror check.

- NEW Sep 18 (this morning): Robert asked for 'new sprint every week' — cron weekly-pmc-sprint created: Mondays 9:30 AM America/New_York, completes prior PMC sprint (incomplete issues back to backlog), creates/starts a new 1-week sprint named 'PMC Sprint — Wk of <date>', pulls all backlog issues in. First run Mon Sep 21 9:30 AM EDT. Jira writes are via browser UI with his SSO session (user-authorized); never API writes.


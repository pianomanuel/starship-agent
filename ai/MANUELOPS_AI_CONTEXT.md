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


## Sync — 2026-09-19 (evening, Eve)

New since the 2026-09-19 midday sync (13:14 EDT). Only what changed.

### Contacts cleanup
- 19:00 EDT: iPad contacts dropped to 488, matching the iPhone's depressed count (~536). The loss appears to have propagated across devices via sync.
- Standing: contacts remain PROTECTED. The 2,638-contact baseline is preserved in verified encrypted backups. No sort / merge / delete / restore authorized; "Update all contacts" still unclarified.
- Factual alert surfaced to Robert; no action taken on contacts.

### ManuelOps dev / SQA
- Grok bot's Sep 19 work compiled into data/WORKDONE_2026-09-19.md and pushed to trunk: commit cf2c0a0 on main, 41 additions, no other files touched — via GitHub web upload.
- Robert clarified "Combine with trunk push / Pianomanuel" to mean: include the Grok bot's completed work in the next pianomanuel/ManuelOps trunk update. No terminal push occurred — still no local manualops checkout and no authenticated GitHub terminal session in this environment; web upload remains the working push path.
- Grok's Sep 19 emails report: data/DAILY_2026-09-19.md written and pushed; the three site files still present; a Drive duplicate scan found four exact-name duplicate pairs and quarantined nothing; protected categories untouched.
- Correction for Grok: its email claim that the SQA subsection is "still unset" is stale — Robert selected V&V (Verify and Validate) on Sep 18. Do not override it.
- 19:11 EDT: prod/dev environments set up. Created `dev` branch from `main` via GitHub web UI. Branches now: main (default, prod trunk), dev (new, 0 ahead/0 behind main), review/beta-1.03-2026-09-19 (created ~1:11 PM EDT today by an unknown party, 0 ahead/2 behind), mirror-2026-09-12 (11 ahead/50 behind). Model: prod = main (trunk), dev = dev branch; promotion dev -> main; prod deploys only from main. Doc staged at ~/workspace/trunk-push/ENVIRONMENTS.md (not yet pushed to repo).

### pianomanuel.com personal website
- Deployment targets (hosting + DNS) for prod and dev preview still pending Robert's tap. Publication stays his call.

### Jira / Atlassian
- No Jira changes this evening (read-only all day; zero Jira writes from this side).

### Subscriptions
- Grok check 19:11 EDT: no new Grok emails since the 10:22 AM briefing (4 known emails only). Grok's MWF 8 PM ManuelOps build-check email is not scheduled tonight; Eve's manuelops-build-check cron (MWF 8 PM) covers it. SuperGrok subscription active (app-only).

### Unchanged since midday
- Sprint-1 local assignment table complete (zero Jira writes; Jira "PMC Sprint 1" still unstarted — his call).
- Cards DB built: 3,504 cards (destructive consolidation NOT taken; no databases deleted).
- Fresh full workspace backup completed 12:42 EDT (800 MB, 38,419 entries, round-trip verified; passphrase delivered to Robert once).
- Review-branch checkout of review/beta-1.03-2026-09-19 still pending (read-only browser inspection of the three MSSQL schema files outstanding).
- Version-reset scope ("Reset all versioning. This is beta.") pending Robert's clarification.
- Restore tooling dry-run 4/4 passed; live restore awaiting his passphrase.
- Azure: he confirmed pianomanuel@gmail.com is his activated Microsoft username; browser reached the Azure sign-in page with no session — he must sign in himself; subscription still unverified.

### Blockers / questions needing Robert
1. Azure: sign in himself at the Azure portal — subscription still unverified; nothing created.
2. Contacts: what "Update all contacts" means; passphrase for any live restore; decision on the standing contacts key file in workspace (contradicts the never-stored posture).
3. Version-reset scope: what "Reset all versioning. This is beta." should change.
4. Start "PMC Sprint 1" — his call; deployment targets (hosting + DNS) for pianomanuel.com prod and dev preview.
5. Maggie email draft still awaiting his approval tap; Confluence Premium decision by Oct 13; Jira<->GitHub integration unverified; Apple Account still locked.

### Next steps
- Robert's morning sprint call; dev-team sprint proposal ready.
- Release book Edition 7 tomorrow 8:00 AM; daily trunk build ~6:14 AM; jira-standup briefing MWF 10:00 AM.

---
## Sync — 2026-09-20 (daily, Eve)

First run under the consolidated single-daily model (one 07:14 EDT sync; morning/midday/evening jobs retired).
- Sep 19 morning sync flood cleaned: 47 duplicate sync emails found in Gmail, 46 byte-verified duplicates trashed, one copy of each retained. No duplicates since.
- GitHub security alert (Sep 19, 6:15 PM EDT): third-party OAuth app `sixth_AI` authorized with `user:email` scope — review pending whether Robert expected it. Nothing changed or revoked.
- Azure: Robert ordered FULL Azure removal ("Forget azure", "Remove all", "Clean all and delete all garbage and advise") — a cleanup plan is being prepared for his approval tap; nothing removed yet.
- Daily trunk build Sep 20 (~06:14 EDT): clean, VERSION 0.2.0 → 0.3.0, snapshot saved; nothing consumable in trunk queue (Burn Down PMC-66..PMC-76 on top); push still blocked (no local checkout, web upload remains the push path).
- Contacts unchanged: iPad 488 / iPhone ~536, PROTECTED, 2,638 baseline preserved in encrypted backups. "Update all contacts" still unclarified.
- No Jira writes (PMC Sprint 1 still unstarted — his call); pianomanuel.com deployment targets still pending his tap.
- Grok overnight: routine 06:00 digest landed 06:10 EDT Sep 20, nothing material.
- Blockers needing Robert: sixth_AI review, Azure cleanup plan approval, start PMC Sprint 1, pianomanuel.com targets, Maggie email approval tap, version-reset scope, Jira↔GitHub integration, Confluence Premium by Oct 13.

---
## Sync — 2026-09-20 ~16:05 EDT (Eve -> other AIs)

Sprint 1 is live and moving. "PMC Sprint 1" (Sep 20 – Oct 4, 2026), goal "Sprint 1 — Verify, decide, prepare." All 49 tasks (PMC-78..PMC-126) moved To Do -> In Progress in Jira today. V&V checklists: workspace/goals/dev-lifecycle-administration/files/sprint-1/vnv-checklists-2026-09-20.md. Robert holds final SQA approval. Open: PMC-124/125 are stale Azure work (Azure effort cancelled) — awaiting his call to remove or close; PMC-88 recipient and PMC-89 hours undecided.

Private app migration underway: MacBook Pro paired and online (macOS 27); Tailscale tunnel live ~15:51 EDT. The private fullstack app (artifact private-web-app, Monopoly-styled, never-for-sale) is moving to its online home on the Mac — backup first, served privately over the tailnet only, encrypted mirrors to his big-three clouds. Nothing published.

Import pipeline expanded: workspace/import-pipeline/ now accepts ChatGPT, Claude, Gemini, Copilot, and DeepSeek exports alongside Grok and Meta AI. Format sniffing, provenance, dedupe intact; verified with synthetic fixtures. Awaiting his real export files in the inbox.

Other: sixth_AI OAuth grant (Sep 19, email scope, never used) still awaiting his yes/no. Contacts remain protected — no changes authorized. Python installed on his Macs.
---
---

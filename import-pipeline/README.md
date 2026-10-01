# Conversation import pipe

A direct pipe for Robert's past conversations from **Grok**, **Meta AI**, and
other AI assistants (**ChatGPT**, **Claude**, **Gemini**, **Copilot**,
**DeepSeek**) into private local storage. Built 2026-09-20; extended to all
AI exports 2026-09-20.

## How it works

1. Robert exports his history (one-time per app, see below).
2. He drops the file into `~/workspace/user/inbox/` — any upload route works.
3. `import_conversations.py` (or the daily watch) parses it into
   `conversations.sqlite3` — deduplicated, timestamped, with source provenance.
4. Eve folds durable facts into memory; the raw history stays private and is
   never published, never merged into contacts/PHI, never sent anywhere.

## Feeding it — Grok

1. Go to grok.x.ai (or the Grok app) → avatar → **Settings → Data Controls**.
2. **Download your data** (or Export your data) → confirm.
3. Wait for the email, download the ZIP, drop it in the inbox.
   (Alternative: X → Settings → Download an archive of your data.)

The pipe reads `export_data/**/prod-grok-backend.json` inside.

## Feeding it — Meta AI

In the Meta AI app, open Settings and look for a data download / export
option; drop whatever it gives (JSON preferred) in the inbox. If the app
offers no export, say so — the fallback is a browser pull with Robert signed in.

## Feeding it — ChatGPT

1. Go to chatgpt.com → profile → **Settings → Data Controls**.
2. **Export data** → confirm the email → download the ZIP.
3. Drop the ZIP in the inbox. The pipe reads `conversations.json` inside
   (mapping-tree format).

## Feeding it — Claude

1. Go to claude.ai → Settings → **Privacy** → export your data.
2. Download the ZIP, drop it in the inbox. The pipe reads
   `conversations.json` (the array with `chat_messages`).

## Feeding it — Gemini

1. Go to Google Takeout (takeout.google.com) → deselect all →
   select **Gemini Apps**.
2. Export, download the ZIP, drop it in the inbox.

## Feeding it — Copilot

1. Go to account.microsoft.com → **Privacy** → download your data.
2. Include Copilot data, download the export, drop it in the inbox.

## Feeding it — DeepSeek

1. In the DeepSeek app/web, open Settings and look for the chat export option.
2. Drop the exported JSON in the inbox.

## Feeding it — anything else

Drop any JSON or Markdown export in the inbox. The pipe sniffs the format,
parses best-effort, and records the parse path in the source provenance
(`parser` column in the `sources` table). Nothing is dropped silently: if no
conversations are recognized, the run report says so.

## Running it

```bash
python3 ~/workspace/import-pipeline/import_conversations.py
```

Re-runnable: already-imported files are skipped by SHA-256; conversations are
unique by (source, source_id). Reports land in `reports/`.

## Privacy

- Store is local-only: `~/workspace/import-pipeline/conversations.sqlite3`.
- Never published, never pushed to GitHub, never mixed into contacts, PHI,
  inbox content, or public site material.
- Encrypted backups only, per the standing rule.

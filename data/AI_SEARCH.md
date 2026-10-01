# AI search map — ManuelOps BETA 2026-09-19

Query the BETA file, not Health bodies.

```sql
SELECT src_table, src_id, title, snippet(ai_search, 3, '[', ']', '…', 12) AS hit
FROM ai_search
WHERE ai_search MATCH 'your words'
LIMIT 20;
```

## Attached tables (sqlite)
circle, idea_card, track, source_file, song, reminder, meta, change_log, ai_search (FTS5)

## Backup
Drive: ManuelOps_BETA_2026-09-19.bak.sqlite (id 1rxJ5smsSfI2EMIYFQYtMWlr8hpkRK8GV)
Drive dump: DUMP_BETA_2026-09-19.sql

## Named workbooks (Drive) — titles only
Seed, Applications, Music, TTS catalog, Documents, Services, MASTER.
Health / Living — flags only; do not ingest notes into FTS.

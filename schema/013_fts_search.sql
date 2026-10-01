-- 013 FTS search for AI (BETA only)
-- Safe tables: circle, meta, change_log, idea_card, track, song, reminder, source_file
-- Do not index Health packets, passwords, Fun-vault, Jim body.

CREATE VIRTUAL TABLE IF NOT EXISTS ai_search USING fts5(
  src_table,
  src_id,
  title,
  body,
  tokenize = 'porter'
);

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'circle', circle_id, circle_name,
       coalesce(purpose,'') || ' ' || coalesce(notes,'') || ' ' || coalesce(primary_tools,'')
FROM circle;

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'meta', key, key, value FROM meta;

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'change_log', printf('%d', id), action, coalesce(detail,'') FROM change_log;

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'idea_card', card_id, card_title, coalesce(work_note,'') FROM idea_card;

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'track', track_id, track, coalesce(next_action,'') || ' ' || coalesce(status_now,'') FROM track;

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'song', song_id, title, coalesce(writers_or_artist,'') || ' ' || coalesce(notes,'') FROM song;

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'reminder', rem_id, title, coalesce(note,'') || ' ' || coalesce(when_text,'') FROM reminder;

INSERT INTO ai_search(src_table, src_id, title, body)
SELECT 'source_file', source_id, coalesce(file_name,''), coalesce(what_it_is,'') || ' ' || coalesce(use_later,'')
FROM source_file;

INSERT INTO change_log(action, approved_by, detail)
VALUES ('fts_013', 'Robert (chat: searchable by ai)', 'ai_search FTS5 on safe tables only');

INSERT OR REPLACE INTO meta(key, value) VALUES
('schema_version', '13'),
('search', 'ai_search FTS5'),
('updated', '2026-09-19');

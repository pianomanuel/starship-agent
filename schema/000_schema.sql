-- ManuelOps primary schema
-- GitHub: pianomanuel/ManuelOps
-- Lock: major changes require Robert approval
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS circle (
  circle_id TEXT PRIMARY KEY,
  circle_name TEXT NOT NULL,
  purpose TEXT,
  resume_section TEXT,
  primary_tools TEXT,
  status TEXT NOT NULL DEFAULT 'Active',
  notes TEXT
);

CREATE TABLE IF NOT EXISTS idea_card (
  card_id TEXT PRIMARY KEY,
  card_title TEXT NOT NULL,
  circle_id TEXT NOT NULL REFERENCES circle(circle_id),
  resume_origin TEXT,
  priority INTEGER,
  next_flag INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'Open',
  work_note TEXT
);

CREATE TABLE IF NOT EXISTS track (
  track_id TEXT PRIMARY KEY,
  track TEXT NOT NULL,
  circle_id TEXT REFERENCES circle(circle_id),
  linked_card TEXT REFERENCES idea_card(card_id),
  resume_status TEXT,
  status_now TEXT NOT NULL DEFAULT 'Open',
  next_action TEXT,
  source_file TEXT
);

CREATE TABLE IF NOT EXISTS source_file (
  source_id TEXT PRIMARY KEY,
  file_name TEXT,
  kind TEXT,
  circle_id TEXT REFERENCES circle(circle_id),
  linked_card TEXT,
  pages_or_size TEXT,
  ingest TEXT,
  sensitivity TEXT,
  what_it_is TEXT,
  use_later TEXT
);

CREATE TABLE IF NOT EXISTS song (
  song_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  writers_or_artist TEXT,
  bpm INTEGER,
  song_key TEXT,
  in_filled_and_fearless INTEGER NOT NULL DEFAULT 0,
  circle_id TEXT REFERENCES circle(circle_id),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS reminder (
  rem_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  when_text TEXT,
  rrule TEXT,
  circle_id TEXT REFERENCES circle(circle_id),
  linked_track TEXT,
  status TEXT NOT NULL DEFAULT 'Open',
  note TEXT
);

CREATE TABLE IF NOT EXISTS change_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  action TEXT NOT NULL,
  approved_by TEXT,
  detail TEXT
);

CREATE INDEX IF NOT EXISTS idx_card_circle ON idea_card(circle_id);
CREATE INDEX IF NOT EXISTS idx_track_circle ON track(circle_id);
CREATE INDEX IF NOT EXISTS idx_song_circle ON song(circle_id);
CREATE INDEX IF NOT EXISTS idx_card_next ON idea_card(next_flag);

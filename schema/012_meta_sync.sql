-- 012 meta sync (2026-09-19)
-- Workaround: 011 already applied as user_version=11. Do not rewrite 011.
-- BETA only. No passwords. No prod overwrite.

INSERT OR REPLACE INTO meta(key, value) VALUES
('updated', '2026-09-19'),
('schema_version', '12'),
('compile_date', '2026-09-19'),
('beta_flag', 'BETA'),
('source_of_truth', 'github site+schema; Drive workbooks; sqlite=BETA only');

INSERT INTO change_log(action, approved_by, detail)
VALUES (
  'meta_sync_012',
  'Robert (chat 2026-09-19: Workaround)',
  'Applied new meta keys without rewriting 011.'
);

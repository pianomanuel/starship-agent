-- ManuelOps meta — source of truth for engine / publish state
-- Load after 000_schema.sql. Does not replace prod without sign-off.
-- No passwords. No connection strings with secrets.

INSERT OR REPLACE INTO meta(key, value) VALUES
('name', 'ManuelOps'),
('parent', 'Life Resume — J. Robert Manuel'),
('lock', 'Major changes require Robert approval'),
('created', '2026-09-11'),
('updated', '2026-09-19'),
('engine', 'sqlite'),
('engine_file', 'ManuelOps.sqlite / ManuelOps_BETA.sqlite'),
('mssql_status', 'schema_only'),
('mssql_schema', 'schema/010_mssql.sql'),
('mssql_promoted', 'no'),
('public_dns', 'off'),
('site_root', 'site/ on GitHub pianomanuel/ManuelOps main'),
('canonical_repo', 'pianomanuel/ManuelOps'),
('archive_repo', 'pianomanuel/SQL'),
('status', 'SEED — not live on pianomanuel.com'),
('azure_hosting', 'blocked_on_subscription'),
('schema_version', '11'),
('compile_date', '2026-09-19'),
('beta_flag', 'BETA'),
('source_of_truth', 'github site+schema; Drive workbooks; sqlite=BETA only');

INSERT INTO change_log(action, approved_by, detail)
VALUES (
  'meta_sync',
  'Robert (chat 2026-09-19: Commit all upgrade beta sync with meta)',
  'schema_version=11 compile_date=2026-09-19 beta_flag=BETA public_dns=off. Runner scripts/migrate_beta.sh. No prod overwrite.'
);

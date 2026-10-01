-- Same meta keys for Microsoft SQL Server (run after 010_mssql.sql).
-- Does not promote MSSQL. Records that promotion has not happened.
USE ManuelOps;
GO
MERGE dbo.meta AS t
USING (VALUES
  (N'name', N'ManuelOps'),
  (N'parent', N'Life Resume — J. Robert Manuel'),
  (N'lock', N'Major changes require Robert approval'),
  (N'created', N'2026-09-11'),
  (N'updated', N'2026-09-19'),
  (N'engine', N'sqlite'),
  (N'engine_file', N'ManuelOps.sqlite / ManuelOps_BETA.sqlite'),
  (N'mssql_status', N'schema_only'),
  (N'mssql_schema', N'schema/010_mssql.sql'),
  (N'mssql_promoted', N'no'),
  (N'public_dns', N'off'),
  (N'site_root', N'site/ on GitHub pianomanuel/ManuelOps main'),
  (N'canonical_repo', N'pianomanuel/ManuelOps'),
  (N'archive_repo', N'pianomanuel/SQL'),
  (N'status', N'SEED — not live on pianomanuel.com'),
  (N'azure_hosting', N'blocked_on_subscription'),
  (N'schema_version', N'11'),
  (N'compile_date', N'2026-09-19'),
  (N'beta_flag', N'BETA'),
  (N'source_of_truth', N'github site+schema; Drive workbooks; sqlite=BETA only')
) AS s([key], [value])
ON t.[key] = s.[key]
WHEN MATCHED THEN UPDATE SET t.[value] = s.[value]
WHEN NOT MATCHED THEN INSERT ([key], [value]) VALUES (s.[key], s.[value]);
GO
INSERT INTO dbo.change_log(action, approved_by, detail)
VALUES (
  N'meta_sync',
  N'Robert (chat 2026-09-19: Commit all upgrade beta sync with meta)',
  N'schema_version=11 compile_date=2026-09-19 beta_flag=BETA public_dns=off. No prod overwrite.'
);
GO

-- 014 MSSQL load — CR-MSSQL-001 signed 2026-09-19
-- Run in SSMS AFTER 010_mssql.sql and 011_meta.mssql.sql
-- Does not contain passwords. Does not drop prod sqlite.
-- FTS skipped on MSSQL per signed defaults.
USE ManuelOps;
GO
SET NOCOUNT ON;

MERGE dbo.circle AS t
USING (VALUES
  (N'CIR-001', N'Music', N'Sacred music, composition, organ/piano/accordion, worship mentoring', N'§1 Music', N'Newzik, Moises Pro, MainStage/Logic, accordion', N'Active', N'Primary identity. Gloria + Magnificat live here.'),
  (N'CIR-002', N'Computers', N'SQA / V&V spine + creative ops (ManuelOps, Vocalis)', N'§2 Computers', N'MSSQL, QTP/ALM thinking, Idea Cards UI', N'Active', N'Secondary spine.'),
  (N'CIR-003', N'Art', N'Rodgon method, anatomy, caricature, faces', N'§3 Art', N'reMarkable, CSP, Procreate, 21 Draw', N'Active', N'2-pages-a-day teach-back. Locked Fun vault stays private.'),
  (N'CIR-004', N'Teaching', N'Natural teacher lane: Geneva, church mentoring, SQA mentoring, draw teach-from', N'§4 Teaching', N'Ear training method, worship team, Rodgon packs', N'Active', N'Geneva method + Impact mentoring.'),
  (N'CIR-005', N'History', N'Places, people, family ledger, synchronicity tags', N'§5 History', N'Photos, Gmail tags, family notes', N'Open', N'Public resume keeps clinical detail private.'),
  (N'CIR-006', N'Living', N'Daily board: practice, flight, health scaffolding, household', N'§6 Current board', N'Reminders, Xbox + DJI Avata, meds routine', N'Active', N'Operating system around the climb.')
) AS s(circle_id, circle_name, purpose, resume_section, primary_tools, status, notes)
ON t.circle_id = s.circle_id
WHEN MATCHED THEN UPDATE SET
  circle_name=s.circle_name, purpose=s.purpose, resume_section=s.resume_section,
  primary_tools=s.primary_tools, status=s.status, notes=s.notes
WHEN NOT MATCHED THEN INSERT
  (circle_id, circle_name, purpose, resume_section, primary_tools, status, notes)
  VALUES (s.circle_id, s.circle_name, s.purpose, s.resume_section, s.primary_tools, s.status, s.notes);
GO

MERGE dbo.meta AS t
USING (VALUES
  (N'engine', N'mssql'),
  (N'mssql_status', N'full'),
  (N'mssql_promoted', N'signed_not_hosted'),
  (N'schema_version', N'14'),
  (N'compile_date', N'2026-09-19'),
  (N'beta_flag', N'BETA'),
  (N'public_dns', N'off'),
  (N'sqlite_mirror', N'ManuelOps_BETA.sqlite'),
  (N'cr', N'CR-MSSQL-001 signed 2026-09-19')
) AS s([key],[value])
ON t.[key] = s.[key]
WHEN MATCHED THEN UPDATE SET t.[value] = s.[value]
WHEN NOT MATCHED THEN INSERT ([key],[value]) VALUES (s.[key], s.[value]);
GO

INSERT INTO dbo.change_log(action, approved_by, detail)
VALUES (
  N'CR-MSSQL-001',
  N'Joseph Robert Manuel IV',
  N'Signed promote scripts. Not executed on a live server from Grok. FTS skipped. sqlite remains mirror.'
);
GO

-- ManuelOps / AILinkHub v2 -- clickable build
-- Roof 2026-09-23: Jira node = PCS (compiled roof). KAN off this seed.
-- Companion only. Does not replace dbo.meta / idea_card. LOCK: not promoted to main.
IF DB_ID(N'AILinkHub') IS NULL CREATE DATABASE AILinkHub;
GO
USE AILinkHub;
GO
SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.MessageLog', N'U') IS NOT NULL DROP TABLE dbo.MessageLog;
IF OBJECT_ID(N'dbo.CommCards', N'U') IS NOT NULL DROP TABLE dbo.CommCards;
IF OBJECT_ID(N'dbo.AIAgents', N'U') IS NOT NULL DROP TABLE dbo.AIAgents;
GO

CREATE TABLE dbo.AIAgents (
  id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_AIAgents PRIMARY KEY,
  name NVARCHAR(50) NOT NULL CONSTRAINT UQ_AIAgents_name UNIQUE,
  type NVARCHAR(20) NOT NULL,
  status NVARCHAR(20) NOT NULL CONSTRAINT DF_AIAgents_status DEFAULT (N'CONNECTED')
);

INSERT INTO dbo.AIAgents (name, type, status) VALUES
  (N'Meta',   N'LLM', N'CONNECTED'),
  (N'Grok',   N'LLM', N'CONNECTED'),
  (N'GitHub', N'VCS', N'CONNECTED'),
  (N'PCS',    N'PM',  N'CONNECTED');

CREATE TABLE dbo.CommCards (
  id NVARCHAR(20) NOT NULL CONSTRAINT PK_CommCards PRIMARY KEY,
  title NVARCHAR(200) NOT NULL,
  from_ai NVARCHAR(50) NULL,
  to_ai NVARCHAR(50) NULL,
  status NVARCHAR(20) NOT NULL CONSTRAINT CK_CommCards_status CHECK (status IN
    (N'pending', N'in_progress', N'linked', N'done', N'new_bug')),
  github_url NVARCHAR(255) NULL,
  jira_url NVARCHAR(120) NULL,
  epic_url NVARCHAR(120) NULL,
  code_hash CHAR(6) NULL,
  is_shared BIT NOT NULL CONSTRAINT DF_CommCards_shared DEFAULT (1),
  reuse_count INT NOT NULL CONSTRAINT DF_CommCards_reuse DEFAULT (0)
);

INSERT INTO dbo.CommCards (id, title, from_ai, to_ai, status, github_url, jira_url, reuse_count) VALUES
  (N'CC-01', N'Roof PCS not KAN', N'Grok', N'PCS', N'linked',
    N'https://github.com/pianomanuel/ManuelOps/issues/27',
    N'https://pianomanuel.atlassian.net/jira/software/projects/PCS/list?jql=project%20%3D%20PCS%20ORDER%20BY%20cf%5B10019%5D%20ASC', 1),
  (N'CC-06', N'mean() NaN on empty set', N'Meta', N'Grok', N'new_bug',
    N'https://github.com/pianomanuel/ManuelOps/issues/23', NULL, 0);

CREATE TABLE dbo.MessageLog (
  id BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_MessageLog PRIMARY KEY,
  card_id NVARCHAR(20) NULL CONSTRAINT FK_MessageLog_card REFERENCES dbo.CommCards(id),
  from_ai NVARCHAR(50) NULL,
  to_ai NVARCHAR(50) NULL,
  message NVARCHAR(MAX) NULL,
  latency_ms INT NULL,
  status NVARCHAR(20) NOT NULL CONSTRAINT DF_MessageLog_status DEFAULT (N'SYNCED'),
  created_at DATETIME2(0) NOT NULL CONSTRAINT DF_MessageLog_ts DEFAULT (SYSUTCDATETIME())
);
GO

CREATE OR ALTER VIEW dbo.vw_SharedCode AS
SELECT
  c.id,
  c.title,
  c.reuse_count,
  CASE
    WHEN COUNT(m.id) = 0 THEN NULL
    ELSE AVG(CAST(m.latency_ms AS FLOAT))
  END AS mean_latency_ms,
  CASE
    WHEN COUNT(m.id) = 0 THEN NULL
    ELSE PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CAST(m.latency_ms AS FLOAT)) OVER (PARTITION BY c.id)
  END AS median_latency_ms
FROM dbo.CommCards AS c
LEFT JOIN dbo.MessageLog AS m ON m.card_id = c.id AND m.latency_ms IS NOT NULL
GROUP BY c.id, c.title, c.reuse_count;
GO
-- CC-06 fix: mean/median stay NULL on empty, never NaN. Live UI should print em-dash, not NaN.

-- ManuelOps Microsoft SQL Server (not SQLite)
-- Database: ManuelOps
-- Run in SSMS / Azure Data Studio.
IF DB_ID(N'ManuelOps') IS NULL CREATE DATABASE ManuelOps;
GO
USE ManuelOps;
GO
SET ANSI_NULLS ON; SET QUOTED_IDENTIFIER ON;
GO
IF OBJECT_ID(N'dbo.reminder', N'U') IS NOT NULL DROP TABLE dbo.reminder;
IF OBJECT_ID(N'dbo.song', N'U') IS NOT NULL DROP TABLE dbo.song;
IF OBJECT_ID(N'dbo.source_file', N'U') IS NOT NULL DROP TABLE dbo.source_file;
IF OBJECT_ID(N'dbo.track', N'U') IS NOT NULL DROP TABLE dbo.track;
IF OBJECT_ID(N'dbo.idea_card', N'U') IS NOT NULL DROP TABLE dbo.idea_card;
IF OBJECT_ID(N'dbo.circle', N'U') IS NOT NULL DROP TABLE dbo.circle;
IF OBJECT_ID(N'dbo.change_log', N'U') IS NOT NULL DROP TABLE dbo.change_log;
IF OBJECT_ID(N'dbo.meta', N'U') IS NOT NULL DROP TABLE dbo.meta;
GO
CREATE TABLE dbo.meta (
  [key] NVARCHAR(80) NOT NULL CONSTRAINT PK_meta PRIMARY KEY,
  [value] NVARCHAR(400) NOT NULL
);
CREATE TABLE dbo.circle (
  circle_id CHAR(7) NOT NULL CONSTRAINT PK_circle PRIMARY KEY,
  circle_name NVARCHAR(40) NOT NULL,
  purpose NVARCHAR(400) NULL,
  resume_section NVARCHAR(40) NULL,
  primary_tools NVARCHAR(200) NULL,
  status NVARCHAR(20) NOT NULL CONSTRAINT DF_circle_status DEFAULT (N'Active'),
  notes NVARCHAR(400) NULL
);
CREATE TABLE dbo.idea_card (
  card_id CHAR(8) NOT NULL CONSTRAINT PK_idea_card PRIMARY KEY,
  card_title NVARCHAR(200) NOT NULL,
  circle_id CHAR(7) NOT NULL CONSTRAINT FK_card_circle REFERENCES dbo.circle(circle_id),
  resume_origin NVARCHAR(80) NULL,
  priority INT NULL,
  next_flag BIT NOT NULL CONSTRAINT DF_card_next DEFAULT (0),
  status NVARCHAR(20) NOT NULL CONSTRAINT DF_card_status DEFAULT (N'Open'),
  work_note NVARCHAR(400) NULL
);
CREATE TABLE dbo.track (
  track_id CHAR(7) NOT NULL CONSTRAINT PK_track PRIMARY KEY,
  track NVARCHAR(80) NOT NULL,
  circle_id CHAR(7) NULL CONSTRAINT FK_track_circle REFERENCES dbo.circle(circle_id),
  linked_card CHAR(8) NULL CONSTRAINT FK_track_card REFERENCES dbo.idea_card(card_id),
  resume_status NVARCHAR(120) NULL,
  status_now NVARCHAR(20) NOT NULL CONSTRAINT DF_track_status DEFAULT (N'Open'),
  next_action NVARCHAR(400) NULL,
  source_file NVARCHAR(260) NULL
);
CREATE TABLE dbo.source_file (
  source_id CHAR(7) NOT NULL CONSTRAINT PK_source PRIMARY KEY,
  file_name NVARCHAR(260) NULL,
  kind NVARCHAR(80) NULL,
  circle_id CHAR(7) NULL CONSTRAINT FK_source_circle REFERENCES dbo.circle(circle_id),
  linked_card CHAR(8) NULL,
  pages_or_size NVARCHAR(40) NULL,
  ingest NVARCHAR(80) NULL,
  sensitivity NVARCHAR(40) NULL,
  what_it_is NVARCHAR(400) NULL,
  use_later NVARCHAR(400) NULL
);
CREATE TABLE dbo.song (
  song_id CHAR(8) NOT NULL CONSTRAINT PK_song PRIMARY KEY,
  title NVARCHAR(160) NOT NULL,
  writers_or_artist NVARCHAR(200) NULL,
  bpm INT NULL,
  song_key NVARCHAR(8) NULL,
  in_filled_and_fearless BIT NOT NULL CONSTRAINT DF_song_ff DEFAULT (0),
  circle_id CHAR(7) NULL CONSTRAINT FK_song_circle REFERENCES dbo.circle(circle_id),
  notes NVARCHAR(400) NULL
);
CREATE TABLE dbo.reminder (
  rem_id CHAR(7) NOT NULL CONSTRAINT PK_reminder PRIMARY KEY,
  title NVARCHAR(200) NOT NULL,
  when_text NVARCHAR(120) NULL,
  rrule NVARCHAR(40) NULL,
  circle_id CHAR(7) NULL CONSTRAINT FK_rem_circle REFERENCES dbo.circle(circle_id),
  linked_track CHAR(7) NULL,
  status NVARCHAR(20) NOT NULL CONSTRAINT DF_rem_status DEFAULT (N'Open'),
  note NVARCHAR(400) NULL
);
CREATE TABLE dbo.change_log (
  id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_change_log PRIMARY KEY,
  ts DATETIME2(0) NOT NULL CONSTRAINT DF_clog_ts DEFAULT (SYSUTCDATETIME()),
  action NVARCHAR(80) NOT NULL,
  approved_by NVARCHAR(200) NULL,
  detail NVARCHAR(800) NULL
);
CREATE INDEX IX_card_circle ON dbo.idea_card(circle_id);
CREATE INDEX IX_card_next ON dbo.idea_card(next_flag);
CREATE INDEX IX_track_circle ON dbo.track(circle_id);
CREATE INDEX IX_song_circle ON dbo.song(circle_id);
GO
-- Seed INSERTs live in project file ManuelOps_MSSQL.sql (full script with data).

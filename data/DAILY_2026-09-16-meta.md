# Meta fix — 2026-09-16

Robert: Fix using meta.

Wrote engine / publish keys into `schema/011_meta.sql` (SQLite) and `schema/011_meta.mssql.sql`.
Compiled readout: `site/meta.html`.

Does not promote MSSQL. Does not turn DNS on. Does not invent a live connection.

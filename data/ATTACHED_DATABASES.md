# Attached databases — SPR-GL-2026-10-10

Attached 2026-09-28. Pointers only. Do not commit sqlite binaries. Do not ingest Health note bodies.
Roof: Google Drive folder ManuelOps `1yVIpYjm18F4X5f2SydVm9NklnGZdWWp8`.
Load path stays `data/ManuelOps_BETA.sqlite` locally. Do not overwrite `ManuelOps.sqlite`.

## Runtime (local / BETA)
- Query file: `ManuelOps_BETA.sqlite` (local). Rebuild from `schema/000_schema.sql` + `schema/001_circles.sql`.
- Drive backup: `ManuelOps_BETA_2026-09-19.bak.sqlite` id `1rxJ5smsSfI2EMIYFQYtMWlr8hpkRK8GV`
- Drive dump: `DUMP_BETA_2026-09-19.sql` id `11QK9ML_743wtgqreNtLM3jUftbMUQOqK`
- Confirm sheet: `ManuelOps_CONFIRM_BETA_1.03_2026-09-19.xlsx` id `1aFyMIgJN4hMeHgQwKxXGkJizPVKB9yuM`

## Named workbooks (one copy each)
| Lane | File | Drive id |
|---|---|---|
| Seed (Sheets) | ManuelOps_Seed_Database_2026-09-11 | `1VwYPCJiQZj4gV9KzuWi9cRkgZ6uEpTPXFgaFXa8HFzk` |
| Seed xlsx | ManuelOps_Seed_Database_2026-09-11.xlsx | `1PjH5-CNTdfNXXc2GpRv2lvQMumvLE14T` |
| Seed PCS | ManuelOps_Seed_Database_2026-09-12_PCS.xlsx | `11Hpl2YzDYn2xcDTvH9dKK2Cn3T37WL3q` |
| Applications | ManuelOps_Applications_Database_2026-09-11.xlsx | `1zEFvuRNn4V5tFj5V9iO2pggkNEzMcSV-` |
| Applications PCS | ManuelOps_Applications_Database_2026-09-12_PCS.xlsx | `1SXaiMf5X1N0bMmUaEU0-M5aX3wzAoQte` |
| Music | ManuelOps_Music_Library_Database_2026-09-11 | `1kYr2MwBV1H387edGVAq6QhoD3wM90s-zOvczCd4QbCM` |
| Documents | ManuelOps_Documents_Database_2026-09-12.xlsx | `1YA4qFJPr68FV07GZngS9dDfLsOsHRHCx` |
| Services | ManuelOps_Services_Database_2026-09-12.xlsx | `1N5h_drxceEexaYl9kEMAtAfemSlpqu1H` |
| TTS catalog | ManuelOps_TTS_Library_Database_2026-09-11 | `18-3TzlxL4o0qdD-a4iTHqrhIPAHAqar7QPJ1sPt-WLE` |
| MASTER (titles) | ManuelOps_MASTER_Database_2026-09-12.xlsx | `14_mf6N9nyP1qizRTEkQvviso6vN-Fnnq` |
| Evening build (latest) | ManuelOps_Evening_Build_Webmaster_2026-09-26.xlsx | `1-bsheSoGgOICnV3xACB9yDSlP7UQkp-B` |

## Flags only — do not attach bodies
- Health / Living workbook title exists on Drive. Flags only. No FTS ingest. No commit of notes.
- Fun-vault, clinical packets, SS amounts, Jim letter body stay Drive-only.

## Not truth
- Duplicate Seed `.2` sheets and older xlsx twins stay retired per MIRROR.md.
- MIRROR-2026-09-12-TEST folder is not a second MASTER.
- Local `favorites.db` / hub session dbs stay gitignored.

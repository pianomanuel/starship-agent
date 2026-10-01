"""Wake/report + verified downloads for pianomanuel hub."""
from __future__ import annotations

import datetime as dt
import shutil
import urllib.parse
from pathlib import Path
from typing import Dict, List

HOME = Path.home()
ORG = HOME / "Documents/Manuel-Organized"


def verified_download_items(kind: str) -> List[Dict]:
    desk = HOME / "Desktop/Gloria-Peters-2026"
    reports = ORG / "Reports-Excel"
    gloria = ORG / "Gloria"
    candidates = []
    if kind in ("downloads", "gloria", "all"):
        candidates += [
            (desk / "Gloria-SATB-Organ-JRM-IV-2026.mxl", "Gloria SATB+Organ .mxl", "clean master"),
            (desk / "Gloria-pack-2026-09-18.zip", "Gloria pack zip", "emailed pack"),
            (desk / "Gloria-Manuel-EditionPeters-2026-09-18.pdf", "Peters sample PDF", "7-page sample"),
            (gloria / "ingest-2026-09-18" / "Gloria-2026-09-05-Full-score.mxl", "Dorico Full-score .mxl", "full source"),
        ]
    if kind in ("downloads", "tags", "all"):
        candidates += [
            (reports / "Tags-Sort-2026-09-18.md", "Tags-Sort report", "markdown"),
            (reports / "MainDB-Index-Rebuild-2026-09-18.md", "MainDB index rebuild", "markdown"),
            (reports / "Wake-Report-latest.pdf", "Latest wake PDF", "status"),
        ]
    items = []
    for path, label, note in candidates:
        try:
            if path.is_file() and path.stat().st_size > 0:
                items.append({
                    "label": label,
                    "note": f"{note} · {path.stat().st_size} bytes",
                    "filename": path.name,
                    "url": "/api/file?path=" + urllib.parse.quote(str(path)),
                })
        except OSError:
            continue
    return items


def write_wake_pdf(summary: str) -> Path:
    out = ORG / "Reports-Excel" / "Wake-Report-latest.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for raw in (summary.splitlines() or ["(empty)"]):
        lines.append(raw[:88])
    content_ops = ["BT /F1 12 Tf 40 760 Td (pianomanuel.com Wake Report) Tj", "0 -16 Td (Verified sources only — no broken streams) Tj"]
    for ln in lines[:42]:
        safe = ln.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_ops.append(f"0 -13 Td ({safe}) Tj")
    content_ops.append("ET")
    stream = "\n".join(content_ops).encode("latin-1", "replace")

    def obj(n, payload: bytes) -> bytes:
        return f"{n} 0 obj\n".encode() + payload + b"\nendobj\n"

    pieces = []
    pieces.append(obj(1, b"<< /Type /Catalog /Pages 2 0 R >>"))
    pieces.append(obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"))
    pieces.append(obj(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"))
    pieces.append(obj(4, b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"))
    pieces.append(obj(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"))

    out_body = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for p in pieces:
        offsets.append(len(out_body))
        out_body += p
    xref_pos = len(out_body)
    out_body += f"xref\n0 {len(offsets)}\n".encode()
    out_body += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out_body += f"{off:010d} 00000 n \n".encode()
    out_body += f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    out.write_bytes(bytes(out_body))
    return out


def wake_report_payload() -> Dict:
    lines = []
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"Wake report — {now} ET")
    try:
        u = shutil.disk_usage(str(HOME))
        lines.append(f"Disk free: {u.free/1e9:.1f} GB of {u.total/1e9:.1f} GB")
    except Exception as e:
        lines.append(f"Disk error: {e}")
    mdb = HOME / "Documents/MainDB"
    for name in ["tags_main.db", "main_thing.db", "index_mirror.db", "health_main.db", "sheet_music.db"]:
        p = mdb / name
        lines.append(f"{name}: {'OK' if p.exists() and p.stat().st_size else 'MISSING'}")
    master = []
    for base in (ORG / "Gloria", HOME / "Documents/PDFs", HOME / "Documents"):
        if base.exists():
            master.extend(list(base.rglob("*MASTER*LOCKED*")))
            if master:
                break
    lines.append(f"Gloria MASTER LOCKED: {'YES' if master else 'NO'}")
    lines.append("Policy: verified downloads only; simultaneous OK; error => Start over")
    summary = "\n".join(lines)
    pdf = write_wake_pdf(summary)
    return {
        "ok": True,
        "summary": summary,
        "pdf_url": "/api/file?path=" + urllib.parse.quote(str(pdf)),
        "pdf_path": str(pdf),
    }



import os as _os
HUB_SEC_DB = Path(_os.environ.get("HUB_SEC_DB", str(HOME / "ManuelOps/hub/secure/security.db")))


def _security_dbs():
    # 2026-09-26: primary store moved to ~/ManuelOps/hub/secure (MainDB is read-only fallback, never written)
    return [
        HUB_SEC_DB,
        HOME / "Documents/MainDB/security.db",
    ]


def hub_account_exists() -> bool:
    import sqlite3
    for db in _security_dbs():
        if not db.exists():
            continue
        try:
            con = sqlite3.connect(str(db))
            try:
                row = con.execute(
                    "SELECT 1 FROM secrets WHERE key='hub_login_hash' AND value IS NOT NULL AND value != ''"
                ).fetchone()
                if row:
                    return True
            finally:
                con.close()
        except Exception:
            continue
    return False


def ensure_security_schema(db: Path) -> None:
    import sqlite3
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db))
    try:
        con.execute(
            "CREATE TABLE IF NOT EXISTS secrets (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        con.commit()
    finally:
        con.close()


def create_hub_account(username: str, password: str, hint: str = "") -> dict:
    """First-run account create. Fails if an account already exists."""
    import hashlib
    import secrets as _secrets
    import sqlite3

    username = (username or "").strip() or "Robert"
    password = password or ""
    if len(password) < 8:
        return {"ok": False, "error": "password too short (min 8)"}
    if hub_account_exists():
        return {"ok": False, "error": "account already exists — sign in instead"}

    salt = _secrets.token_hex(16)
    hash_hex = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    hint = (hint or "local hub").strip()[:80]

    for db in (HUB_SEC_DB,):
        ensure_security_schema(db)
        con = sqlite3.connect(str(db))
        try:
            for k, v in (
                ("hub_login_salt", salt),
                ("hub_login_hash", hash_hex),
                ("hub_login_hint", hint),
                ("hub_login_user", username),
            ):
                con.execute(
                    "INSERT INTO secrets(key, value) VALUES(?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (k, v),
                )
            con.commit()
        finally:
            con.close()
    return {"ok": True, "user": username, "hint": hint}

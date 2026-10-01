#!/usr/bin/env python3
"""Monopoly hub — HTTP :8080 + HTTPS :8444, Apple-style session login."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import ssl
import subprocess
import threading
import time
import urllib.parse
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional
import hub_extras
import favorites_store  # 2026-09-26 favorites/links DB (bookmark manager)

ROOT = Path(os.environ.get("HUB_ROOT", str(Path.home() / "ManuelOps/hub/root"))).resolve()
HOME = Path.home()
ORG = HOME / "Documents/Manuel-Organized"
BOARD = ORG / "Monopoly-Board"
SEC_DB = Path(os.environ.get("HUB_SEC_DB", str(HOME / "ManuelOps/hub/secure/security.db")))
MAIN_SEC = HOME / "Documents/MainDB/security.db"
CERT = Path(os.environ.get("HUB_CERT", str(HOME / "ManuelOps/hub/certs/main_thing.crt")))
KEY = Path(os.environ.get("HUB_KEY", str(HOME / "ManuelOps/hub/certs/main_thing.key")))
VAULT = ORG / "Secure/NSFW-Vault"
SPARSE = HOME / "Library/CloudStorage/OneDrive-Personal/Documents/Disk Images/Fun-Conversations-Locked.sparsebundle"
ONEDRIVE_DOCS = HOME / "Library/CloudStorage/OneDrive-Personal/Documents"
CLOUD_BACKUP = ONEDRIVE_DOCS / "ManuelOps-Documents-CloudBackup"
FUN_VOL_CANDIDATES = [
    Path("/Volumes/Fun Conversations Locked"),
    Path("/Volumes/Fun-Conversations-Locked"),
]
HOST = "127.0.0.1"
HTTP_PORT = int(os.environ.get("HUB_HTTP_PORT", "8080"))
HTTPS_PORT = int(os.environ.get("HUB_HTTPS_PORT", "8444"))
COOKIE = "hub_sess"
SESSION_TTL = int(os.environ.get("HUB_SESSION_TTL", str(30 * 24 * 3600)))  # 30 days (2026-09-26)
SESSIONS = {}  # in-memory cache: token -> expiry (persisted in SESSIONS_DB)
SESSIONS_DB = Path(os.environ.get("HUB_SESSIONS_DB", str(Path(os.environ.get("HUB_SEC_DB", str(Path.home() / "ManuelOps/hub/secure/security.db"))).parent / "sessions.db")))
_SDB_LOCK = threading.Lock()


def _sdb():
    SESSIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(SESSIONS_DB), timeout=5)
    con.execute("CREATE TABLE IF NOT EXISTS sessions (token_sha256 TEXT PRIMARY KEY, created REAL NOT NULL, expires REAL NOT NULL)")
    try:
        os.chmod(SESSIONS_DB, 0o600)
    except OSError:
        pass
    return con


def _th(tok: str) -> str:
    return hashlib.sha256(tok.encode("utf-8")).hexdigest()


def drop_session(tok: Optional[str]) -> None:
    if not tok:
        return
    SESSIONS.pop(tok, None)
    with _SDB_LOCK:
        con = _sdb()
        try:
            con.execute("DELETE FROM sessions WHERE token_sha256=?", (_th(tok),)); con.commit()
        finally:
            con.close()
LOGIN_LOCK = threading.Lock()
FAILS = {"n": 0, "until": 0.0}

PUBLIC_EXACT = {
    "/api/account-status",
    "/api/create-account",
    "/login",
    "/logout",
    "/api/login",
    "/css/hub.css",
    "/favicon.ico",
    "/apple-touch-icon.png",
    "/apple-touch-icon-precomposed.png",
}
PUBLIC_PREFIX = ("/css/",)

FUN_README = """# Fun Conversations Locked

Volume attach password is in Secure/security.db (vault_password) for Ventnor/NSFW only.
Hub opens this tree silently via POST /api/open-nsfw — no web password UI.

Desktop: Fun-Conversations-Locked.sparsebundle → OneDrive Disk Images.
"""


def write_fun_readme(vol: Optional[Path]):
    try:
        if vol and vol.exists():
            (vol / "README-UNLOCK.md").write_text(FUN_README, encoding="utf-8")
    except Exception:
        pass


def fun_vol() -> Optional[Path]:
    for p in FUN_VOL_CANDIDATES:
        if p.exists():
            return p
    return None


def get_nsfw_password() -> str:
    """NSFW / Ventnor sparsebundle only — from security.db. Fail closed (no hardcoded fallback)."""
    for db in (SEC_DB, MAIN_SEC):
        if db.exists():
            con = sqlite3.connect(str(db))
            try:
                row = con.execute(
                    "SELECT value FROM secrets WHERE key='vault_password'"
                ).fetchone()
                if row and row[0]:
                    return row[0]
            finally:
                con.close()
    raise RuntimeError("vault_password missing from security.db")


def load_hub_login():
    salt = hash_hex = hint = ""
    for db in (SEC_DB, MAIN_SEC):
        if not db.exists():
            continue
        con = sqlite3.connect(str(db))
        try:
            def g(k):
                r = con.execute("SELECT value FROM secrets WHERE key=?", (k,)).fetchone()
                return r[0] if r and r[0] else ""
            salt = salt or g("hub_login_salt")
            hash_hex = hash_hex or g("hub_login_hash")
            hint = hint or g("hub_login_hint")
        finally:
            con.close()
        if salt and hash_hex:
            break
    return salt, hash_hex, hint


def check_hub_password(pw: str) -> bool:
    salt, hash_hex, _ = load_hub_login()
    if not salt or not hash_hex or not pw:
        return False
    got = hashlib.sha256((salt + pw).encode("utf-8")).hexdigest()
    return hmac.compare_digest(got.lower(), hash_hex.lower())


def new_session() -> str:
    tok = secrets.token_urlsafe(32)
    now = time.time()
    SESSIONS[tok] = now + SESSION_TTL
    with _SDB_LOCK:
        con = _sdb()
        try:
            con.execute("DELETE FROM sessions WHERE expires < ?", (now,))
            con.execute("INSERT OR REPLACE INTO sessions VALUES (?,?,?)", (_th(tok), now, now + SESSION_TTL)); con.commit()
        finally:
            con.close()
    return tok


def valid_session(tok: Optional[str]) -> bool:
    if not tok:
        return False
    exp = SESSIONS.get(tok)
    if not exp:
        with _SDB_LOCK:
            con = _sdb()
            try:
                row = con.execute("SELECT expires FROM sessions WHERE token_sha256=?", (_th(tok),)).fetchone()
            finally:
                con.close()
        if not row:
            return False
        exp = SESSIONS[tok] = float(row[0])
    if exp < time.time():
        drop_session(tok)
        return False
    return True


def card_subs_map() -> Dict[str, Dict[str, Path]]:
    """Per-card subfolder keys → absolute paths (Finder open targets)."""
    return {
        "boardwalk": {
            "Issues": BOARD / "Boardwalk/Issues",
            "Reports": BOARD / "Boardwalk/Reports",
        },
        "park-place": {
            "Ops": BOARD / "Park-Place/Ops",
            "MainDB": BOARD / "Park-Place/MainDB",
            "CoS-Mirror": BOARD / "Park-Place/CoS-Mirror",
        },
        "pacific": {
            "Sheet-Music": BOARD / "Pacific/Sheet-Music",
            "Cleaned-PDF": BOARD / "Pacific/Cleaned-PDF",
            "MusicXML": BOARD / "Pacific/MusicXML",
            "MIDI": BOARD / "Pacific/MIDI",
        },
        "north-carolina": {
            "MusicXML": BOARD / "North-Carolina/MusicXML",
            "To-Newzik": BOARD / "North-Carolina/To-Newzik",
        },
        "st-charles": {
            "Photos": BOARD / "St-Charles/Photos",
            "People-Places": BOARD / "St-Charles/People-Places",
        },
        "electric": {
            "Main-Thing": BOARD / "Electric/Main-Thing",
            "API": BOARD / "Electric/API",
        },
        "reading": {
            "UCC": BOARD / "Reading/UCC",
        },
        "mediterranean": {
            "Public-Records": BOARD / "Mediterranean/Public-Records",
        },
        "baltic": {
            "Health": BOARD / "Baltic/Health",
            "Medical-Records": BOARD / "Baltic/Medical-Records",
            "Health-Research": BOARD / "Baltic/Health-Research",
        },
        "oriental": {
            "Circles": BOARD / "Oriental/Circles",
        },
        "virginia": {
            "Contacts": BOARD / "Virginia/Contacts",
            "Piano-Resumes": BOARD / "Virginia/Piano-Resumes",
            "Piano-Gigs": BOARD / "Virginia/Piano-Gigs",
        },
        "new-york": {
            "Bookmarks": BOARD / "New-York/Bookmarks",
        },
        "illinois": {
            "Crossref": BOARD / "Illinois/Crossref",
        },
        "atlantic": {
            "Vehicles": BOARD / "Atlantic/Vehicles",
            "Vehicles-Research": BOARD / "Atlantic/Vehicles-Research",
        },
        "pennsylvania": {
            "Music-Research": BOARD / "Pennsylvania/Music-Research",
        },
        "ventnor": {
            "NSFW-Vault": BOARD / "Ventnor/NSFW-Vault",
        },
        "states": {
            "Photos-People-Places": BOARD / "States/Photos-People-Places",
            "Reports": BOARD / "States/Reports",
        },
        "vermont": {
            "OneDrive": BOARD / "Vermont/OneDrive",
            "CloudBackup": BOARD / "Vermont/CloudBackup",
            "Reports": BOARD / "Vermont/Reports",
        },
        "chance": {
            "AI-Cross": BOARD / "Chance/AI-Cross",
            "Reports": BOARD / "Chance/Reports",
        },
        "ai-cross": {
            "AI-Cross": BOARD / "Chance/AI-Cross",
            "Reports": BOARD / "Chance/Reports",
        },
    }


def card_paths(cid: str, sub: Optional[str] = None) -> List[Path]:
    """Default open targets for a card; optional sub key opens that sub only."""
    cid = (cid or "").strip().lower()
    subs = card_subs_map().get(cid, {})
    if sub:
        sub = sub.strip()
        # normalize aliases
        aliases = {
            "issues": "Issues", "reports": "Reports", "ops": "Ops", "maindb": "MainDB",
            "cos-mirror": "CoS-Mirror", "cos_mirror": "CoS-Mirror", "sheet-music": "Sheet-Music",
            "cleaned-pdf": "Cleaned-PDF", "musicxml": "MusicXML", "midi": "MIDI",
            "to-newzik": "To-Newzik", "photos": "Photos", "people-places": "People-Places",
            "main-thing": "Main-Thing", "api": "API", "ucc": "UCC",
            "public-records": "Public-Records", "health": "Health",
            "medical-records": "Medical-Records", "health-research": "Health-Research",
            "circles": "Circles", "contacts": "Contacts", "piano-resumes": "Piano-Resumes",
            "piano-gigs": "Piano-Gigs", "bookmarks": "Bookmarks", "crossref": "Crossref",
            "vehicles": "Vehicles", "vehicles-research": "Vehicles-Research",
            "music-research": "Music-Research", "nsfw-vault": "NSFW-Vault",
            "photos-people-places": "Photos-People-Places", "onedrive": "OneDrive",
            "cloudbackup": "CloudBackup", "cloud-backup": "CloudBackup",
            "ai-cross": "AI-Cross", "ai_cross": "AI-Cross",
        }
        key = aliases.get(sub.lower(), sub)
        if key in subs:
            return [subs[key]]
        # try exact case-insensitive match
        for k, p in subs.items():
            if k.lower() == sub.lower():
                return [p]
        return []

    mapping = {
        "boardwalk": [BOARD / "Boardwalk/Issues", ORG / "Reports-Excel"],
        "park-place": [BOARD / "Park-Place/Ops", HOME / "Documents/MainDB", BOARD / "Park-Place/CoS-Mirror"],
        "pacific": [BOARD / "Pacific/Sheet-Music", ORG / "Sheet-Music"],
        "illinois": [BOARD / "Illinois/Crossref", ROOT / "crossref_index.html"],
        "new-york": [BOARD / "New-York/Bookmarks", ORG / "Bookmarks"],
        "st-charles": [BOARD / "St-Charles/Photos", ORG / "Photos-Intelligent"],
        "oriental": [BOARD / "Oriental/Circles", HOME / "Documents/MainDB/circles_of_joy.db"],
        "oriental-db": [HOME / "Documents/MainDB/circles_of_joy.db", BOARD / "Oriental/Circles"],
        "electric": [BOARD / "Electric/Main-Thing", HOME / "Documents/MainDB"],
        "reading": [BOARD / "Reading/UCC", ROOT / "ucc-react"],
        "mediterranean": [BOARD / "Mediterranean/Public-Records", HOME / "Documents/MainDB/public_records.db"],
        "mediterranean-db": [HOME / "Documents/MainDB/public_records.db", BOARD / "Mediterranean/Public-Records"],
        "baltic": [BOARD / "Baltic/Health", BOARD / "Baltic/Health-Research", ORG / "Health-Research", ORG / "Health", HOME / "Documents/MainDB/medical_records.db"],
        "baltic-db": [HOME / "Documents/MainDB/medical_records.db", BOARD / "Baltic/Medical-Records"],
        "atlantic": [BOARD / "Atlantic/Vehicles", BOARD / "Atlantic/Vehicles-Research", ORG / "Vehicles-Research"],
        "pennsylvania": [BOARD / "Pennsylvania/Music-Research", ORG / "Music-Research"],
        "virginia": [BOARD / "Virginia/Contacts", ORG / "Contacts", BOARD / "Virginia/Piano-Resumes", BOARD / "Virginia/Piano-Gigs"],
        "north-carolina": [BOARD / "North-Carolina/MusicXML", ORG / "Sheet-Music/MusicXML", BOARD / "North-Carolina/To-Newzik"],
        "states": [BOARD / "States/Photos-People-Places", HOME / "Documents/MainDB/photos_people_places.db", BOARD / "States/Reports"],
        "vermont": [BOARD / "Vermont/OneDrive", BOARD / "Vermont/CloudBackup", HOME / "Documents/MainDB/onedrive_main.db", CLOUD_BACKUP],
        "chance": [BOARD / "Chance/AI-Cross", HOME / "Documents/MainDB/ai_cross.db", ROOT / "data/ai_cross.json"],
        "ai-cross": [BOARD / "Chance/AI-Cross", HOME / "Documents/MainDB/ai_cross.db", ROOT / "data/ai_cross.json"],
    }
    return mapping.get(cid, [])


def ventnor_paths() -> List[Path]:
    fv = fun_vol()
    return [fv, VAULT] if fv else [VAULT]


def ensure_fun_mounted(pw: str) -> list:
    notes = []
    if fun_vol() is not None:
        notes.append("already-mounted")
        return notes
    if not SPARSE.exists():
        notes.append("sparsebundle-missing")
        return notes
    plist, bck = SPARSE / "Info.plist", SPARSE / "Info.bckup"
    if not plist.exists() and bck.exists():
        plist.write_bytes(bck.read_bytes())
        notes.append("restored-Info.plist")
    p = subprocess.run(
        ["hdiutil", "attach", "-stdinpass", str(SPARSE)],
        input=pw.encode(),
        capture_output=True,
        timeout=120,
    )
    notes.append("hdiutil-rc=%s" % p.returncode)
    if p.returncode != 0:
        notes.append((p.stderr or b"").decode()[:240])
    return notes


def open_paths(paths) -> list:
    opened = []
    for p in paths:
        if p is None:
            continue
        p = Path(p)
        if not p.exists():
            if p.suffix == "":
                p.mkdir(parents=True, exist_ok=True)
            else:
                continue
        subprocess.run(["open", str(p)], check=False)
        opened.append(str(p))
    return opened


def open_ventnor():
    try:
        pw = get_nsfw_password()
    except RuntimeError as e:
        return {"ok": False, "error": str(e), "opened": [], "notes": ["vault_password missing"]}
    notes = ensure_fun_mounted(pw)
    VAULT.mkdir(parents=True, exist_ok=True)
    vol = fun_vol()
    write_fun_readme(vol)
    opened = open_paths(ventnor_paths())
    return {"ok": True, "opened": opened, "notes": notes}


def resolve_open_path(raw: str) -> Optional[Path]:
    """Allow opening only under ORG, MainDB, BOARD, or OneDrive Documents."""
    if not raw or ".." in raw:
        return None
    p = Path(raw).expanduser()
    if not p.is_absolute():
        # treat as relative to BOARD or ORG
        for base in (BOARD, ORG, HOME / "Documents/MainDB"):
            cand = (base / raw).resolve()
            if str(cand).startswith(str(base.resolve())):
                p = cand
                break
    try:
        p = p.resolve()
    except Exception:
        return None
    allowed = [
        BOARD.resolve(),
        ORG.resolve(),
        (HOME / "Documents/MainDB").resolve(),
        ONEDRIVE_DOCS.resolve(),
        ROOT.resolve(),
    ]
    for a in allowed:
        try:
            if str(p).startswith(str(a)):
                return p
        except Exception:
            continue
    return None


LOGIN_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="theme-color" content="#0a0b0e" />
  <title>Sign in — pianomanuel.com</title>
  <link rel="stylesheet" href="/css/hub.css?v=20260926s" />
</head>
<body class="login-body">
  <div class="login-wrap">
    <div class="login-card glass">
      <div class="login-lights"><span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span></div>
      <p class="login-kicker">ManuelOps</p>
      <h1 class="mark login-title">pianomanuel.com</h1>
      <p class="login-sub">Sign in to continue</p>
      <div class="login-avatar" aria-hidden="true">RM</div>
      <p class="login-name">Robert Manuel</p>
      <form id="f" class="login-form" method="post" action="/api/login" autocomplete="current-password">
        <label class="login-label" for="pw">Password</label>
        <input id="pw" name="password" type="password" class="login-input" autofocus required />
        <button type="submit" class="login-btn" id="go">Sign In</button>
        <p class="login-err" id="err" hidden>Incorrect password. Try again.</p>
        <p class="login-hint">__HINT__</p>
      </form>
    </div>
  </div>
  <script>
    const f = document.getElementById("f");
    const err = document.getElementById("err");
    const go = document.getElementById("go");
    f.addEventListener("submit", async (e) => {
      e.preventDefault();
      err.hidden = true;
      go.disabled = true;
      const pw = document.getElementById("pw").value;
      try {
        const r = await fetch("/api/login", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "same-origin",
          body: JSON.stringify({password: pw})
        });
        if (r.ok) {
          const n = new URLSearchParams(location.search).get("next") || "/site/";
          location.replace(n.startsWith("/") ? n : "/");
          return;
        }
        err.hidden = false;
        document.getElementById("pw").focus();
        document.getElementById("pw").select();
      } catch (x) {
        err.hidden = false;
      }
      go.disabled = false;
    });
  </script>
</body>
</html>
"""


CREATE_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#0a0b0e" />
  <title>Create your password — pianomanuel.com</title>
  <link rel="stylesheet" href="/css/hub.css?v=20260926s" />
</head>
<body class="login-body">
  <div class="login-wrap">
    <div class="login-card glass">
      <div class="login-lights"><span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span></div>
      <p class="login-kicker">ManuelOps · first run</p>
      <h1 class="mark login-title">pianomanuel.com</h1>
      <p class="login-sub">Create your password</p>
      <div class="login-avatar" aria-hidden="true">RM</div>
      <p class="login-name">Robert Manuel</p>
      <form id="f" class="login-form" method="post" action="/api/create-account" autocomplete="off">
        <label class="login-label" for="pw">New password</label>
        <input id="pw" name="password" type="password" class="login-input" autocomplete="new-password" minlength="8" autofocus required />
        <label class="login-label" for="pw2">Confirm password</label>
        <input id="pw2" name="confirm" type="password" class="login-input" autocomplete="new-password" minlength="8" required />
        <button type="submit" class="login-btn" id="go">Create Password</button>
        <p class="login-err" id="err" hidden></p>
        <p class="login-hint">At least 8 characters. Stored as a salted hash on this Mac only.</p>
      </form>
    </div>
  </div>
  <script>
    const f = document.getElementById("f"), err = document.getElementById("err"), go = document.getElementById("go");
    function show(m){ err.textContent = m; err.hidden = false; }
    f.addEventListener("submit", async (e) => {
      e.preventDefault(); err.hidden = true;
      const pw = document.getElementById("pw").value, pw2 = document.getElementById("pw2").value;
      if (pw.length < 8) return show("Use at least 8 characters.");
      if (pw !== pw2) return show("Passwords don't match.");
      go.disabled = true;
      try {
        const r = await fetch("/api/create-account", {method: "POST", headers: {"Content-Type": "application/json"},
          credentials: "same-origin", body: JSON.stringify({user: "Robert", password: pw, hint: "local hub"})});
        const j = await r.json().catch(() => ({}));
        if (r.ok && j.ok) {
          const n = new URLSearchParams(location.search).get("next") || "/site/";
          location.replace(n.startsWith("/") ? n : "/site/"); return;
        }
        if (r.status === 409) { location.reload(); return; }
        show(j.error || "Could not create the account.");
      } catch (x) { show("Network error. Try again."); }
      go.disabled = false;
    });
  </script>
</body>
</html>
"""


class HubHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, fmt, *a):
        try:
            line = "%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), fmt % a)
            logp = HOME / "Library/Logs/pianomanel-hub-access.log"
            logp.parent.mkdir(parents=True, exist_ok=True)
            with open(logp, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass

    def is_https(self) -> bool:
        return bool(getattr(self.server, "is_ssl", False))

    def cookie_tok(self) -> Optional[str]:
        raw = self.headers.get("Cookie") or ""
        c = SimpleCookie()
        try:
            c.load(raw)
        except Exception:
            return None
        morsel = c.get(COOKIE)
        return morsel.value if morsel else None

    def authed(self) -> bool:
        return valid_session(self.cookie_tok())

    def is_public(self, path: str) -> bool:
        if path in PUBLIC_EXACT:
            return True
        return path.startswith(PUBLIC_PREFIX)

    def blocked_file(self, path: str) -> bool:
        low = path.lower()
        if low.endswith((".py", ".pyc", ".db", ".key", ".pem", ".crt")):
            return True
        base = path.rsplit("/", 1)[-1]
        if base.startswith(".") and path not in ("/",):
            return True
        return False

    def wants_html_redirect(self, path: str) -> bool:
        """HTTP→HTTPS for HTML-ish GETs when Host is pianomanuel.com (keep API on HTTP)."""
        if self.is_https():
            return False
        host = (self.headers.get("Host") or "").split(":")[0].lower()
        if host not in ("pianomanuel.com", "www.pianomanuel.com"):
            return False
        if path.startswith("/api/"):
            return False
        accept = (self.headers.get("Accept") or "").lower()
        if path.endswith((".html", ".htm", "/")) or path in ("/", "/login", "/logout"):
            return True
        if "text/html" in accept and not path.startswith("/css/") and not path.startswith("/data/"):
            # modules etc without extension unlikely; still redirect bare paths
            if "." not in path.rsplit("/", 1)[-1]:
                return True
        return False

    def _send(self, code, body: bytes, ctype: str, extra=None, extra_headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        if extra:
            extra()
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code, obj, extra=None, extra_headers=None):
        body = json.dumps(obj).encode()
        self._send(code, body, "application/json", extra=extra, extra_headers=extra_headers)

    def set_session_cookie(self, tok: str):
        parts = [
            "%s=%s" % (COOKIE, tok),
            "Path=/",
            "HttpOnly",
            "SameSite=Lax",
            "Max-Age=%d" % SESSION_TTL,
        ]
        if self.is_https():
            parts.append("Secure")
        self.send_header("Set-Cookie", "; ".join(parts))

    def clear_session_cookie(self):
        parts = ["%s=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0" % COOKIE]
        if self.is_https():
            parts.append("Secure")
        self.send_header("Set-Cookie", "; ".join(parts))

    def redirect(self, loc, extra=None, code=302):
        body = b""
        def hdr():
            self.send_header("Location", loc)
            if extra:
                extra()
        self._send(code, body, "text/plain", extra=hdr)

    def serve_login(self):
        # First run (2026-09-26): no account row -> show the create-password form instead of sign-in.
        if not hub_extras.hub_account_exists():
            self._send(200, CREATE_HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        disk = ROOT / "login.html"
        if disk.exists():
            self._send(200, disk.read_bytes(), "text/html; charset=utf-8")
            return
        _, _, hint = load_hub_login()
        html = LOGIN_HTML.replace("__HINT__", (hint or "Apple-style hub gate").replace("<", ""))
        self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "https://pianomanuel.com:8444")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path or "/"
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        # Force secure UI: any non-HTTPS HTML page → https://pianomanuel.com:8444
        if self.command == "GET" and not self.is_https():
            if path.startswith("/api/"):
                pass  # APIs may stay on current scheme for tooling
            elif path.startswith("/css/"):
                pass
            else:
                q = ("?" + parsed.query) if parsed.query else ""
                loc = "https://pianomanuel.com:%d%s%s" % (HTTPS_PORT, path if path != "/" else "/", q)
                return self.redirect(loc, code=302)

        # Never serve secrets via static file handler
        low = path.lower()
        if any(x in low for x in ("security.db", "passwords.csv", "chrome-import-passwords", "/secure/", "vault_password")):
            self.send_error(404)
            return


        if path == "/api/account-status":
            exists = hub_extras.hub_account_exists()
            return self._json(200, {"ok": True, "exists": exists, "mode": "signin" if exists else "create"})

        if path == "/logout":
            tok = self.cookie_tok()
            if tok:
                drop_session(tok)
            return self.redirect("/login", extra=self.clear_session_cookie)

        if path == "/login":
            if self.authed():
                return self.redirect("/site/")
            return self.serve_login()

        if self.blocked_file(path):
            return self.send_error(404)

        if not self.is_public(path) and not self.authed():
            if path.startswith("/api/"):
                return self._json(401, {"ok": False, "error": "login required"})
            nxt = path if path != "/" else "/site/"
            try:
                with open(HOME / "Library/Logs/pianomanel-hub-auth.log", "a", encoding="utf-8") as _f:
                    _f.write("%s auth-miss path=%s cookie_present=%s session_known=%s sec_fetch_site=%s ua=%s\n" % (
                        time.strftime("%Y-%m-%d %H:%M:%S"), path, bool(self.cookie_tok()), False,
                        self.headers.get("Sec-Fetch-Site", "-"), (self.headers.get("User-Agent") or "-")[:60]))
            except Exception:
                pass
            return self.redirect("/login?next=" + urllib.parse.quote(nxt))


        if path == "/api/links":
            # 2026-09-26 Bookmark Manager: list/search/filter favorites.db (auth required above)
            qs = urllib.parse.parse_qs(parsed.query or "")
            one = lambda k, d="": ((qs.get(k) or [d])[0]).strip()
            tri = lambda k: None if one(k) == "" else one(k) in ("1", "true", "yes")
            try:
                return self._json(200, favorites_store.list_links(q=one("q"), folder=one("folder"), tag=one("tag"),
                    favorite=tri("favorite"), protected=tri("protected"), archived=one("archived") in ("1", "true"),
                    limit=int(one("limit", "200") or 200), offset=int(one("offset", "0") or 0)))
            except Exception as e:
                return self._json(500, {"ok": False, "error": "links query failed", "detail": str(e)[:200]})

        if path == "/api/verified-downloads":
            qs = urllib.parse.parse_qs(parsed.query or "")
            kind = ((qs.get("kind") or ["downloads"])[0]).strip().lower()
            items = hub_extras.verified_download_items(kind)
            return self._json(200, {"ok": True, "items": items, "policy": "verified-only; simultaneous OK; no resume streams"})

        if path == "/api/file":
            qs = urllib.parse.parse_qs(parsed.query or "")
            raw = ((qs.get("path") or [""])[0]).strip()
            resolved = resolve_open_path(raw)
            if not resolved or not resolved.is_file():
                return self._json(404, {"ok": False, "error": "not a verified file"})
            data = resolved.read_bytes()  # full read — no chunked resume / no break-continue stream
            ctype = "application/octet-stream"
            if resolved.suffix.lower() == ".pdf":
                ctype = "application/pdf"
            elif resolved.suffix.lower() in (".html", ".htm"):
                ctype = "text/html; charset=utf-8"
            elif resolved.suffix.lower() in (".md", ".txt"):
                ctype = "text/plain; charset=utf-8"
            elif resolved.suffix.lower() in (".mxl", ".musicxml", ".xml"):
                ctype = "application/vnd.recordare.musicxml+xml"
            elif resolved.suffix.lower() == ".zip":
                ctype = "application/zip"
            def hdr():
                fn = resolved.name.replace(chr(34), "")
                self.send_header("Content-Disposition", f"attachment; filename=\"{fn}\"")
            return self._send(200, data, ctype, extra=hdr)

        if path == "/api/card-subs":
            qs = urllib.parse.parse_qs(parsed.query or "")
            cid = ((qs.get("card") or [""])[0]).strip().lower()
            if not cid:
                all_map = {k: list(v.keys()) for k, v in card_subs_map().items()}
                return self._json(200, {"ok": True, "cards": all_map})
            subs = card_subs_map().get(cid)
            if subs is None:
                return self._json(404, {"ok": False, "error": "unknown card"})
            items = []
            for name, p in subs.items():
                items.append({"sub": name, "path": str(p), "exists": p.exists()})
            return self._json(200, {"ok": True, "card": cid, "subs": items})

        if path == "/":
            return self.redirect("/site/")
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = (parsed.path or "/").rstrip("/") or "/"
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        ctype = (self.headers.get("Content-Type") or "").lower()



        if path in ("/logout", "/api/logout"):
            tok = self.cookie_tok()
            if tok:
                drop_session(tok)
            # JSON clients get JSON; others redirect
            accept = (self.headers.get("Accept") or "").lower()
            ctype = (self.headers.get("Content-Type") or "").lower()
            if "application/json" in accept or "application/json" in ctype or path.startswith("/api/"):
                return self._json(200, {"ok": True}, extra=self.clear_session_cookie)
            return self.redirect("/login", extra=self.clear_session_cookie)



        if path == "/api/create-account":
            if hub_extras.hub_account_exists():
                return self._json(409, {"ok": False, "error": "account already exists — sign in instead"})
            try:
                data = json.loads(raw.decode() or "{}") if raw else {}
            except json.JSONDecodeError:
                return self._json(400, {"ok": False, "error": "bad json"})
            user = str(data.get("user") or data.get("username") or "Robert")
            pw = str(data.get("password") or data.get("pass") or "")
            hint = str(data.get("hint") or "local hub")
            result = hub_extras.create_hub_account(user, pw, hint)
            if not result.get("ok"):
                return self._json(400, result)
            tok = new_session()
            return self._json(200, result, extra=lambda: self.set_session_cookie(tok))

        if path == "/api/login" or path == "/login":
            pw = ""
            if "application/json" in ctype:
                try:
                    data = json.loads(raw.decode() or "{}")
                except json.JSONDecodeError:
                    return self._json(400, {"ok": False, "error": "bad json"})
                pw = str(data.get("password") or "")
            else:
                form = urllib.parse.parse_qs(raw.decode("utf-8", "replace"))
                pw = (form.get("password") or [""])[0]
            with LOGIN_LOCK:
                now = time.time()
                if now < FAILS["until"]:
                    return self._json(429, {"ok": False, "error": "try again shortly"})
                ok = check_hub_password(pw)
                if not ok:
                    FAILS["n"] += 1
                    if FAILS["n"] >= 5:
                        FAILS["until"] = now + 30
                        FAILS["n"] = 0
                    return self._json(401, {"ok": False, "error": "incorrect"})
                FAILS["n"] = 0
            tok = new_session()
            if "application/json" in ctype or self.headers.get("Accept", "").find("json") >= 0:
                return self._json(200, {"ok": True}, extra=lambda: self.set_session_cookie(tok))
            return self.redirect("/site/", extra=lambda: self.set_session_cookie(tok))

        if not self.authed():
            return self._json(401, {"ok": False, "error": "login required"})

        try:
            data = json.loads(raw.decode() or "{}") if raw else {}
        except json.JSONDecodeError:
            return self._json(400, {"ok": False, "error": "bad json"})


        if path in ("/api/links/add", "/api/links/edit", "/api/links/favorite", "/api/links/archive", "/api/links/restore"):
            # 2026-09-26 Bookmark Manager writes. Archive is a soft delete (archived=1); rows are never removed.
            if not isinstance(data, dict):
                return self._json(400, {"ok": False, "error": "bad body"})
            try:
                fn = {"/api/links/add": favorites_store.add_link, "/api/links/edit": favorites_store.edit_link,
                      "/api/links/favorite": favorites_store.toggle_favorite, "/api/links/archive": favorites_store.archive_link,
                      "/api/links/restore": lambda d: favorites_store.archive_link(d, restore=True)}[path]
                res = fn(data)
                return self._json(200 if res.get("ok") else 400, res)
            except Exception as e:
                return self._json(500, {"ok": False, "error": "links update failed", "detail": str(e)[:200]})

        if path == "/api/wake-report":
            try:
                return self._json(200, hub_extras.wake_report_payload())
            except Exception as e:
                return self._json(500, {"ok": False, "error": "wake failed — use Start over", "detail": str(e)})

        if path == "/api/open-nsfw":
            return self._json(200, open_ventnor())

        if path == "/api/open-card":
            cid = (data.get("card") or "").strip().lower()
            sub = (data.get("sub") or "").strip() or None
            if cid in ("ventnor", "nsfw") and not sub:
                return self._json(200, open_ventnor())
            if cid in ("ventnor", "nsfw") and sub:
                # Never silently mount via sub pointer alone — require open-nsfw / full card
                return self._json(400, {"ok": False, "error": "use /api/open-nsfw for Ventnor vault"})
            paths = card_paths(cid, sub)
            if not paths:
                return self._json(404, {"ok": False, "error": "unknown card or sub"})
            return self._json(200, {"ok": True, "card": cid, "sub": sub, "opened": open_paths(paths)})

        if path == "/api/open-sub":
            cid = (data.get("card") or "").strip().lower()
            sub = (data.get("sub") or "").strip()
            if not cid or not sub:
                return self._json(400, {"ok": False, "error": "card and sub required"})
            if cid in ("ventnor", "nsfw"):
                return self._json(400, {"ok": False, "error": "use /api/open-nsfw for Ventnor vault"})
            paths = card_paths(cid, sub)
            if not paths:
                return self._json(404, {"ok": False, "error": "unknown card or sub"})
            return self._json(200, {"ok": True, "card": cid, "sub": sub, "opened": open_paths(paths)})

        if path == "/api/open-path":
            raw_path = (data.get("path") or data.get("p") or "").strip()
            resolved = resolve_open_path(raw_path)
            if not resolved:
                return self._json(403, {"ok": False, "error": "path not allowed"})
            return self._json(200, {"ok": True, "opened": open_paths([resolved])})

        self.send_error(404)


def _serve(httpd, label):
    print(label, flush=True)
    httpd.serve_forever()


def main():
    os.chdir(ROOT)
    httpd = ThreadingHTTPServer((HOST, HTTP_PORT), HubHandler)
    httpd.is_ssl = False
    httpsd = ThreadingHTTPServer((HOST, HTTPS_PORT), HubHandler)
    httpsd.is_ssl = True
    if not CERT.exists() or not KEY.exists():
        raise SystemExit("missing hub certs: %s / %s" % (CERT, KEY))
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(str(CERT), str(KEY))
    httpsd.socket = ctx.wrap_socket(httpsd.socket, server_side=True)
    threading.Thread(
        target=_serve,
        args=(httpd, "hub http://pianomanuel.com:%s/" % HTTP_PORT),
        daemon=True,
    ).start()
    _serve(httpsd, "hub https://pianomanuel.com:%s/" % HTTPS_PORT)


if __name__ == "__main__":
    main()

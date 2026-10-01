"""favorites.db store: schema, URL normalization and the queries behind the hub's
/api/links endpoints. Delete is a soft archive only (archived=1). 2026-09-26."""
import os, sqlite3, time, urllib.parse
from pathlib import Path

DB_PATH = Path(os.environ.get("HUB_FAVORITES_DB", str(Path.home() / "Documents/MainDB/favorites.db")))

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS folders(
  id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, parent_id INTEGER REFERENCES folders(id),
  protected INTEGER NOT NULL DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS tags(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS links(
  id INTEGER PRIMARY KEY, url TEXT NOT NULL, url_norm TEXT NOT NULL UNIQUE, title TEXT,
  folder_id INTEGER REFERENCES folders(id), source_browser TEXT,
  favorite INTEGER NOT NULL DEFAULT 0, protected INTEGER NOT NULL DEFAULT 0, archived INTEGER NOT NULL DEFAULT 0,
  added_at TEXT, updated_at TEXT, last_checked TEXT, status TEXT DEFAULT 'unchecked', source TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS link_tags(
  link_id INTEGER NOT NULL REFERENCES links(id), tag_id INTEGER NOT NULL REFERENCES tags(id), PRIMARY KEY(link_id,tag_id));
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
CREATE INDEX IF NOT EXISTS idx_links_folder ON links(folder_id);
CREATE INDEX IF NOT EXISTS idx_links_fav ON links(favorite,archived);
CREATE VIEW IF NOT EXISTS links_v AS
  SELECT l.*, f.name AS folder, (SELECT group_concat(t.name, ',') FROM link_tags lt JOIN tags t ON t.id=lt.tag_id WHERE lt.link_id=l.id) AS tags
  FROM links l LEFT JOIN folders f ON f.id=l.folder_id;
"""

_DROP_Q = ("utm_", "fbclid", "gclid", "mc_eid", "mc_cid")

def norm_url(u: str):
    """Normalize for de-duplication: lowercase scheme/host, drop default port,
    fragment, tracking params and a trailing slash. Returns None for unusable URLs."""
    u = (u or "").strip()
    if not u or u.startswith(("javascript:", "data:", "about:", "chrome:", "place:")):
        return None
    try:
        p = urllib.parse.urlsplit(u)
    except ValueError:
        return None
    scheme = p.scheme.lower()
    if scheme not in ("http", "https", "file", "ftp", "smb", "afp", "mailto"):
        return None
    host = (p.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    port = p.port if p.port and not ((scheme == "http" and p.port == 80) or (scheme == "https" and p.port == 443)) else None
    netloc = host + (":%d" % port if port else "")
    path = p.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True) if not k.lower().startswith(_DROP_Q)]
    query = urllib.parse.urlencode(sorted(q))
    return urllib.parse.urlunsplit(("http" if scheme == "https" else scheme, netloc, path, query, ""))

def connect(path=None):
    db = sqlite3.connect(str(path or DB_PATH), timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db

def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")

def _row(r):
    d = dict(r); d.pop("url_norm", None)
    d["tags"] = [t for t in (d.get("tags") or "").split(",") if t]
    return d

def list_links(q="", folder="", tag="", favorite=None, protected=None, archived=False, limit=200, offset=0):
    if not DB_PATH.exists():
        return {"ok": False, "error": "favorites.db not found", "path": str(DB_PATH)}
    where, args = ["archived=?"], [1 if archived else 0]
    if q:
        where.append("(title LIKE ? OR url LIKE ? OR IFNULL(tags,'') LIKE ? OR IFNULL(notes,'') LIKE ?)"); args += ["%" + q + "%"] * 4
    if folder:
        where.append("folder=?"); args.append(folder)
    if tag:
        where.append("(','||IFNULL(tags,'')||',') LIKE ?"); args.append("%," + tag + ",%")
    if favorite is not None:
        where.append("favorite=?"); args.append(1 if favorite else 0)
    if protected is not None:
        where.append("protected=?"); args.append(1 if protected else 0)
    limit = max(1, min(int(limit), 1000)); offset = max(0, int(offset))
    with connect() as db:
        w = " AND ".join(where)
        total = db.execute("SELECT count(*) FROM links_v WHERE " + w, args).fetchone()[0]
        rows = db.execute("SELECT * FROM links_v WHERE " + w + " ORDER BY protected DESC, favorite DESC, lower(title) LIMIT ? OFFSET ?", args + [limit, offset]).fetchall()
        folders = [dict(r) for r in db.execute("SELECT f.name, f.protected, count(l.id) AS n FROM folders f LEFT JOIN links l ON l.folder_id=f.id AND l.archived=0 GROUP BY f.id ORDER BY f.protected DESC, f.name")]
        tags = [r[0] for r in db.execute("SELECT name FROM tags ORDER BY name")]
        counts = dict(db.execute("SELECT 'active', count(*) FROM links WHERE archived=0 UNION ALL SELECT 'favorite', count(*) FROM links WHERE archived=0 AND favorite=1 UNION ALL SELECT 'protected', count(*) FROM links WHERE archived=0 AND protected=1 UNION ALL SELECT 'archived', count(*) FROM links WHERE archived=1").fetchall())
    return {"ok": True, "total": total, "items": [_row(r) for r in rows], "folders": folders, "tags": tags, "counts": counts}

def _folder_id(db, name):
    name = (name or "").strip()
    if not name:
        return None
    db.execute("INSERT OR IGNORE INTO folders(name,created_at) VALUES(?,?)", (name, _now()))
    return db.execute("SELECT id FROM folders WHERE name=?", (name,)).fetchone()[0]

def _set_tags(db, lid, tags):
    db.execute("DELETE FROM link_tags WHERE link_id=?", (lid,))
    for t in tags:
        t = t.strip().lower()[:40]
        if not t:
            continue
        db.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (t,))
        tid = db.execute("SELECT id FROM tags WHERE name=?", (t,)).fetchone()[0]
        db.execute("INSERT OR IGNORE INTO link_tags VALUES(?,?)", (lid, tid))

def _tags_in(v):
    if isinstance(v, str):
        v = v.split(",")
    return [str(x) for x in (v or [])][:20]

def add_link(data):
    url = (data.get("url") or "").strip()
    n = norm_url(url)
    if not n:
        return {"ok": False, "error": "invalid url"}
    with connect() as db:
        ex = db.execute("SELECT id, archived FROM links WHERE url_norm=?", (n,)).fetchone()
        if ex:
            return {"ok": False, "error": "duplicate", "id": ex["id"], "archived": bool(ex["archived"])}
        cur = db.execute("INSERT INTO links(url,url_norm,title,folder_id,source_browser,favorite,protected,added_at,updated_at,status,source,notes) VALUES(?,?,?,?,?,?,0,?,?,'unchecked','hub',?)",
                         (url, n, (data.get("title") or url)[:500], _folder_id(db, data.get("folder")), (data.get("source_browser") or "manual")[:40],
                          1 if data.get("favorite") else 0, _now(), _now(), (data.get("notes") or "")[:2000] or None))
        _set_tags(db, cur.lastrowid, _tags_in(data.get("tags")))
        return {"ok": True, "id": cur.lastrowid}

def edit_link(data):
    lid = int(data.get("id") or 0)
    with connect() as db:
        r = db.execute("SELECT * FROM links WHERE id=?", (lid,)).fetchone()
        if not r:
            return {"ok": False, "error": "not found"}
        sets, args = [], []
        if "url" in data:
            n = norm_url(data["url"])
            if not n:
                return {"ok": False, "error": "invalid url"}
            other = db.execute("SELECT id FROM links WHERE url_norm=? AND id!=?", (n, lid)).fetchone()
            if other:
                return {"ok": False, "error": "duplicate", "id": other["id"]}
            sets += ["url=?", "url_norm=?"]; args += [data["url"].strip(), n]
        if "title" in data:
            sets.append("title=?"); args.append((data["title"] or "")[:500])
        if "folder" in data:
            sets.append("folder_id=?"); args.append(_folder_id(db, data["folder"]))
        if "notes" in data:
            sets.append("notes=?"); args.append((data["notes"] or "")[:2000] or None)
        if "favorite" in data:
            sets.append("favorite=?"); args.append(1 if data["favorite"] else 0)
        if sets:
            db.execute("UPDATE links SET " + ", ".join(sets) + ", updated_at=? WHERE id=?", args + [_now(), lid])
        if "tags" in data:
            _set_tags(db, lid, _tags_in(data["tags"]))
        return {"ok": True, "id": lid}

def toggle_favorite(data):
    lid = int(data.get("id") or 0)
    with connect() as db:
        r = db.execute("SELECT favorite FROM links WHERE id=?", (lid,)).fetchone()
        if not r:
            return {"ok": False, "error": "not found"}
        v = 0 if r["favorite"] else 1
        db.execute("UPDATE links SET favorite=?, updated_at=? WHERE id=?", (v, _now(), lid))
        return {"ok": True, "id": lid, "favorite": bool(v)}

def archive_link(data, restore=False):
    """Soft delete only: sets archived=1 (or 0 to restore). Rows are never removed.
    Protected links cannot be archived from the hub."""
    lid = int(data.get("id") or 0)
    with connect() as db:
        r = db.execute("SELECT protected FROM links WHERE id=?", (lid,)).fetchone()
        if not r:
            return {"ok": False, "error": "not found"}
        if r["protected"] and not restore:
            return {"ok": False, "error": "protected link: archive refused"}
        db.execute("UPDATE links SET archived=?, updated_at=? WHERE id=?", (0 if restore else 1, _now(), lid))
        return {"ok": True, "id": lid, "archived": not restore}

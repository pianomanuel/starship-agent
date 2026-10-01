#!/usr/bin/env python3
"""Conversation import pipe — AI chat history into a private local store.

Drop an export into ~/workspace/user/inbox/ (zip or extracted folder) and run:
    python3 import_conversations.py
or let the daily watch cron do it unattended.

Supported inputs (best-effort, vendor formats change without notice):
  - Grok:      export_data/**/prod-grok-backend.json (grok.x.ai > avatar >
               Settings > Data Controls > Download your data, or the X archive)
  - ChatGPT:   conversations.json (chatgpt.com > Settings > Data Controls >
               Export data) — mapping-tree format
  - Claude:    conversations.json (claude.ai > Settings > Privacy > export) —
               array with chat_messages
  - Gemini:    Google Takeout "Gemini Apps" JSON drop
  - Copilot:   Microsoft privacy-dashboard Copilot export (JSON)
  - DeepSeek:  DeepSeek chat export (JSON)
  - Meta AI:   a JSON chat export dropped in the inbox (generic parser)
  - Any:       *.md pasted conversations (stored as one conversation per file)
  - Fallback:  any other JSON is imported best-effort with the generic parser
               and the parse path is recorded in the source provenance.

Storage: conversations.sqlite3 next to this script. Private, sandboxed, never
published, never merged into contacts/PHI/public content. Re-runnable:
files are deduplicated by SHA-256, conversations by (source, source_id).
"""
import hashlib
import json
import sqlite3
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PIPE_DIR = Path(__file__).resolve().parent
INBOX = Path.home() / "workspace" / "user" / "inbox"
DB = PIPE_DIR / "conversations.sqlite3"
REPORTS = PIPE_DIR / "reports"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    origin_path TEXT NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    imported_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT,
    created_at TEXT,
    message_count INTEGER DEFAULT 0,
    UNIQUE(source, source_id)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    sender TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT,
    model TEXT,
    text_hash TEXT NOT NULL,
    UNIQUE(conversation_id, text_hash)
);
"""

# Later-added provenance columns (harmless if already present).
MIGRATIONS = [
    "ALTER TABLE sources ADD COLUMN parser TEXT",
]


def ts_to_iso(v):
    """MongoDB extended JSON {$date: {$numberLong: ms}} / unix / ISO -> ISO."""
    try:
        if isinstance(v, dict):
            d = v.get("$date", v)
            if isinstance(d, dict):
                ms = int(d.get("$numberLong", 0))
            else:
                ms = int(d)
        elif isinstance(v, (int, float)):
            ms = int(v)
            if ms < 10_000_000_000:  # seconds, not ms
                ms *= 1000
        elif isinstance(v, str):
            return v
        else:
            return None
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return None


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_sender(role) -> str:
    r = str(role or "").strip().lower()
    if r in ("user", "human", "me", "end-user"):
        return "human"
    return "assistant"


# ---------------------------------------------------------------- parsers
# Every parser returns a list of (source_id, title, created_at, turns) where
# turns = list of (sender, text, created_at, model).

def parse_grok_conversations(convs):
    out = []
    for c in convs:
        if not isinstance(c, dict):
            continue
        conv = c.get("conversation", c) if isinstance(c.get("conversation"), dict) else c
        cid = str(conv.get("id") or conv.get("conversation_id") or "")
        if not cid:
            continue
        title = conv.get("title")
        created = ts_to_iso(conv.get("create_time") or conv.get("created_at"))
        turns = []
        responses = c.get("responses") if isinstance(c.get("responses"), list) else []
        for r in responses:
            resp = r.get("response", r) if isinstance(r, dict) else {}
            if not isinstance(resp, dict):
                continue
            sender = "human" if str(resp.get("sender", "")).lower() == "human" else "assistant"
            turns.append((sender, resp.get("message", ""),
                          ts_to_iso(resp.get("create_time")), resp.get("model")))
        out.append((cid, title, created, turns))
    return out


def parse_chatgpt(data):
    """ChatGPT conversations.json: list of {id, title, create_time, mapping}."""
    convs = data if isinstance(data, list) else data.get("conversations", [])
    out = []
    for c in convs:
        if not isinstance(c, dict):
            continue
        cid = str(c.get("id") or c.get("conversation_id") or "")
        if not cid:
            continue
        title = c.get("title")
        created = ts_to_iso(c.get("create_time") or c.get("created_at"))
        mapping = c.get("mapping") if isinstance(c.get("mapping"), dict) else {}
        nodes = []
        for n in mapping.values():
            if not isinstance(n, dict):
                continue
            m = n.get("message")
            if not isinstance(m, dict):
                continue
            role = str((m.get("author") or {}).get("role") or m.get("role") or "").lower()
            if role not in ("user", "assistant", "system", "human"):
                continue
            content = m.get("content") or {}
            parts = content.get("parts") if isinstance(content, dict) else []
            text = "\n".join(p for p in (parts or []) if isinstance(p, str))
            if not text.strip():
                continue
            sender = "human" if role in ("user", "human") else "assistant"
            ct = m.get("create_time") or 0
            try:
                ct = float(ct)
            except Exception:
                ct = 0
            nodes.append((ct, sender, text,
                          ts_to_iso(m.get("create_time")),
                          content.get("model") if isinstance(content, dict) else None))
        nodes.sort(key=lambda x: x[0])
        turns = [(s, t, ts, mo) for _, s, t, ts, mo in nodes]
        out.append((cid, title, created, turns))
    return out


def parse_claude(data):
    """Claude export: array of {uuid, name, created_at, chat_messages[{sender,text}]}."""
    convs = data if isinstance(data, list) else data.get("conversations", [])
    out = []
    for c in convs:
        if not isinstance(c, dict):
            continue
        cid = str(c.get("uuid") or c.get("id") or "")
        if not cid:
            continue
        title = c.get("name") or c.get("title")
        created = ts_to_iso(c.get("created_at") or c.get("created"))
        msgs = c.get("chat_messages") or []
        turns = []
        for m in msgs if isinstance(msgs, list) else []:
            if not isinstance(m, dict):
                continue
            sender = "human" if str(m.get("sender", "")).lower() == "human" else "assistant"
            text = m.get("text") or ""
            if isinstance(text, list):
                text = "\n".join(b.get("text", "") for b in text if isinstance(b, dict))
            turns.append((sender, str(text),
                          ts_to_iso(m.get("created_at") or m.get("timestamp")),
                          m.get("model")))
        out.append((cid, title, created, turns))
    return out


def message_list_turns(msgs):
    """Shared helper: parse a flat list of message dicts."""
    turns = []
    for m in msgs if isinstance(msgs, list) else []:
        if not isinstance(m, dict):
            continue
        sender = norm_sender(m.get("role") or m.get("sender") or m.get("author"))
        text = m.get("content") or m.get("text") or m.get("message") or ""
        if isinstance(text, list):  # content blocks
            text = "\n".join(b.get("text", "") for b in text if isinstance(b, dict))
        turns.append((sender, str(text),
                      ts_to_iso(m.get("timestamp") or m.get("created_at")
                                or m.get("date") or m.get("time")),
                      m.get("model")))
    return turns


def parse_flat_chats(data, extra_keys=()):
    """Generic shape: {chats|conversations|threads|sessions: [{id,title,messages}]}.
    Fallback index labels each chat as <stem>-<i> so nothing is dropped."""
    convs = []
    if isinstance(data, dict):
        for key in ("chats", "conversations", "threads", "sessions", "topics") + tuple(extra_keys):
            if isinstance(data.get(key), list):
                convs = data[key]
                break
        if not convs:
            # best-effort: descend into a lone list-of-dicts value so odd
            # vendor shapes are not dropped silently
            for v in data.values():
                if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
                    convs = v
                    break
        if not convs:
            convs = [data]
    elif isinstance(data, list):
        convs = data
    out = []
    for i, ch in enumerate(convs):
        if not isinstance(ch, dict):
            continue
        cid = str(ch.get("id") or ch.get("uuid") or ch.get("conversation_id")
                  or ch.get("session_id") or ch.get("thread_id") or f"chat-{i}")
        title = ch.get("title") or ch.get("name")
        created = ts_to_iso(ch.get("created_at") or ch.get("created")
                            or ch.get("create_time") or ch.get("timestamp"))
        msgs = ch.get("messages") or ch.get("turns") or ch.get("chat_messages") or []
        out.append((cid, title, created, message_list_turns(msgs)))
    return out


def sniff_format(data, filename: str) -> str:
    """Best-effort format classifier. Never raises; returns 'generic' unknown."""
    try:
        name = filename.lower()
        if "prod-grok-backend" in name:
            return "grok"

        items = []
        if isinstance(data, list):
            items = [x for x in data if isinstance(x, dict)][:5]
        elif isinstance(data, dict):
            for key in ("conversations", "chats", "threads", "sessions"):
                if isinstance(data.get(key), list):
                    items = [x for x in data[key] if isinstance(x, dict)][:5]
                    break

        if items:
            first = items[0]
            if isinstance(first.get("mapping"), dict):
                return "chatgpt"                     # mapping tree = ChatGPT export
            if isinstance(first.get("chat_messages"), list):
                return "claude"                      # chat_messages = Claude export
            if first.get("uuid") and "name" in first:
                return "claude"

        def any_role(roles):
            for it in items:
                msgs = it.get("messages") if isinstance(it, dict) else None
                if isinstance(msgs, list):
                    for m in msgs:
                        if isinstance(m, dict) and str(m.get("role", "")).lower() in roles:
                            return True
            return False

        for token, fmt in (("chatgpt", "chatgpt"), ("claude", "claude"),
                           ("gemini", "gemini"), ("takeout", "gemini"),
                           ("copilot", "copilot"), ("deepseek", "deepseek"),
                           ("meta", "meta_ai")):
            if token in name:
                return fmt
        if any_role(("model",)):
            return "gemini"
        if isinstance(data, dict) and any(k in data for k in ("sessions", "topics")):
            return "deepseek"
        if "meta" in name:
            return "meta_ai"
        return "generic"
    except Exception:
        return "generic"


PARSERS = {
    "grok": ("grok", parse_grok_conversations),
    "chatgpt": ("chatgpt", parse_chatgpt),
    "claude": ("claude", parse_claude),
    "gemini": ("gemini", lambda d: parse_flat_chats(d)),
    "copilot": ("copilot", lambda d: parse_flat_chats(d)),
    "deepseek": ("deepseek", lambda d: parse_flat_chats(d)),
    "meta_ai": ("meta_ai", lambda d: parse_flat_chats(d)),
    "generic": ("generic", lambda d: parse_flat_chats(d)),
}
# ----------------------------------------------------------------


class Importer:
    def __init__(self):
        self.con = sqlite3.connect(DB)
        self.con.executescript(SCHEMA)
        for ddl in MIGRATIONS:
            try:
                self.con.execute(ddl)
            except sqlite3.OperationalError:
                pass
        self.stats = {"sources": 0, "conversations": 0, "messages": 0, "skipped_dup": 0}

    def register_source(self, source, origin_path, digest, parser=None):
        cur = self.con.execute(
            "INSERT OR IGNORE INTO sources (source, origin_path, sha256, imported_at, parser)"
            " VALUES (?,?,?,?,?)",
            (source, str(origin_path), digest,
             datetime.now(timezone.utc).isoformat(), parser),
        )
        self.con.commit()
        if cur.rowcount:
            self.stats["sources"] += 1
            return True
        self.stats["skipped_dup"] += 1
        return False

    def add_conversation(self, source, source_id, title, created_at, turns):
        """turns: list of (sender, text, created_at, model). Returns True if new."""
        cur = self.con.execute(
            "INSERT OR IGNORE INTO conversations (source, source_id, title, created_at)"
            " VALUES (?,?,?,?)",
            (source, source_id, title, created_at),
        )
        if not cur.rowcount:
            return False
        cid = cur.lastrowid
        n = 0
        for sender, text, ts, model in turns:
            if not text:
                continue
            th = hashlib.sha256(f"{sender}|{text}".encode()).hexdigest()
            mc = self.con.execute(
                "INSERT OR IGNORE INTO messages"
                " (conversation_id, sender, text, created_at, model, text_hash)"
                " VALUES (?,?,?,?,?,?)",
                (cid, sender, text, ts, model, th),
            )
            n += mc.rowcount
        self.con.execute(
            "UPDATE conversations SET message_count=? WHERE id=?", (n, cid))
        self.con.commit()
        self.stats["conversations"] += 1
        self.stats["messages"] += n
        return True

    def import_json(self, path: Path):
        """Detect the AI format, parse, and store. Nothing is dropped silently:
        unknown shapes fall back to the generic parser and the format is logged."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            return f"unreadable: {e}"
        fmt = sniff_format(data, path.name)
        source, parser = PARSERS[fmt]
        digest = sha256_file(path)
        if not self.register_source(source, path, digest, parser=fmt):
            return f"[{fmt}] already imported"
        try:
            if source == "grok":
                convs = data.get("conversations") if isinstance(data, dict) else data
                parsed = parser(convs if isinstance(convs, list) else [])
            else:
                parsed = parser(data)
        except Exception as e:
            return f"[{fmt}] parse error: {e}"
        added = 0
        for cid, title, created, turns in parsed:
            if self.add_conversation(source, cid, title, created, turns):
                added += 1
        if not added and not parsed:
            return f"[{fmt}] ok, no conversations recognized (best-effort generic tried)"
        return f"[{fmt}] ok, {added} new conversations"

    def import_markdown(self, path: Path, source="pasted"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not self.register_source(source, path, digest := sha256_file(path), parser="markdown"):
            return "[markdown] already imported"
        self.add_conversation(source, f"{path.stem}", path.stem, None,
                              [("human", text, None, None)])
        return "[markdown] ok, stored as one conversation"

    def scan(self):
        results = []
        if not INBOX.exists():
            return ["inbox missing"]
        # unpack zips first (into a sibling dir, keep the zip as the source record)
        for zp in sorted(INBOX.glob("*.zip")):
            dest = INBOX / (zp.stem + "_extracted")
            if not dest.exists():
                try:
                    with zipfile.ZipFile(zp) as z:
                        z.extractall(dest)
                    results.append(f"unzipped {zp.name}")
                except Exception as e:
                    results.append(f"zip failed {zp.name}: {e}")
        # JSON drops anywhere in the inbox, incl. extracted exports
        for jp in sorted(INBOX.rglob("*.json")):
            results.append(f"json {jp.name}: {self.import_json(jp)}")
        # markdown drops (top level only, as before)
        for mp in sorted(INBOX.glob("*.md")):
            results.append(f"md {mp.name}: {self.import_markdown(mp)}")
        return results

    def report(self, results):
        REPORTS.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        cur = self.con.execute(
            "SELECT source, COUNT(*), COALESCE(SUM(message_count),0) FROM conversations GROUP BY source")
        lines = [f"# Conversation import report — {stamp}", ""]
        for src, nconv, nmsg in cur.fetchall():
            lines.append(f"- {src}: {nconv} conversations, {nmsg} messages")
        if not self.stats["conversations"] and not self.stats["sources"]:
            lines.append("- (store currently empty)")
        lines += ["", "## This run", ""]
        lines += [f"- {r}" for r in results] or ["- nothing new in inbox"]
        s = self.stats
        lines.append(f"- new: {s['sources']} sources, {s['conversations']} conversations,"
                     f" {s['messages']} messages; skipped duplicates: {s['skipped_dup']}")
        rp = REPORTS / f"import-report-{stamp}.md"
        rp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return rp


def main():
    imp = Importer()
    results = imp.scan()
    rp = imp.report(results)
    print("\n".join(results))
    print(f"report: {rp}")
    print(f"db: {DB}")


if __name__ == "__main__":
    sys.exit(main())

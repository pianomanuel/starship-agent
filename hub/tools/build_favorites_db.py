#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
"""Build/seed favorites.db (links, folders, tags). 2026-09-26.
Sources (read-only): bookmarks_main.db (MainDB), the Netscape export that holds
"★ ManuelOps (Protected)" + "Favorites (cleaned)", and optional browser source
files used only to tag source_browser. Never writes to any source.
Usage: build_favorites_db.py OUT_DB [--bookmarks DB] [--netscape HTML] [--srcdir DIR]
Refuses to overwrite an existing OUT_DB unless --force (then the old file is kept as .bak-<ts>)."""
import argparse, html, json, os, plistlib, shutil, sqlite3, sys, time
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))
from favorites_store import SCHEMA, norm_url, connect  # noqa: E402

class Netscape(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack=[]; self.pending=None; self.in_h3=False; self.in_a=None; self.items=[]; self.buf=""
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="h3": self.in_h3=True; self.buf=""
        elif tag=="dl": self.stack.append(self.pending or ""); self.pending=None
        elif tag=="a": self.in_a=a; self.buf=""
    def handle_endtag(self, tag):
        if tag=="h3": self.in_h3=False; self.pending=self.buf.strip()
        elif tag=="dl" and self.stack: self.stack.pop()
        elif tag=="a" and self.in_a is not None:
            self.items.append((self.in_a.get("href",""), self.buf.strip(), [s for s in self.stack if s], self.in_a.get("add_date"))); self.in_a=None
    def handle_data(self, d):
        if self.in_h3 or self.in_a is not None: self.buf+=d

def browser_map(srcdir):
    m={}
    if not srcdir or not Path(srcdir).is_dir(): return m
    def add(u,b): 
        n=norm_url(u)
        if n: m.setdefault(n,set()).add(b)
    for f in Path(srcdir).glob("chrome__*.json"):
        try: d=json.loads(f.read_text())
        except Exception: continue
        def walk(n):
            if n.get("type")=="url": add(n.get("url",""),"chrome")
            for c in n.get("children",[]) or []: walk(c)
        for r in (d.get("roots") or {}).values():
            if isinstance(r,dict): walk(r)
    for f in Path(srcdir).glob("safari__*.plist"):
        try: d=plistlib.loads(f.read_bytes())
        except Exception: continue
        def walk(n):
            if isinstance(n,dict):
                if n.get("URLString"): add(n["URLString"],"safari")
                for c in n.get("Children",[]) or []: walk(c)
        walk(d)
    return m

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--bookmarks"); ap.add_argument("--netscape"); ap.add_argument("--srcdir"); ap.add_argument("--force",action="store_true")
    a=ap.parse_args(); out=Path(a.out).expanduser()
    if out.exists():
        if not a.force: sys.exit("refusing: %s exists (use --force)"%out)
        shutil.copy2(out, str(out)+".bak-"+time.strftime("%Y%m%d-%H%M%S")); out.unlink()
    db=connect(out); db.executescript(SCHEMA)
    now=time.strftime("%Y-%m-%dT%H:%M:%S%z"); bmap=browser_map(a.srcdir)
    stats={"seen":0,"inserted":0,"dup_merged":0,"skipped_invalid":0,"from_bookmarks_db":0,"from_netscape":0}
    def folder_id(name, protected=0):
        if not name: return None
        db.execute("INSERT OR IGNORE INTO folders(name,protected,created_at) VALUES(?,?,?)",(name,protected,now))
        if protected: db.execute("UPDATE folders SET protected=1 WHERE name=?",(name,))
        return db.execute("SELECT id FROM folders WHERE name=?",(name,)).fetchone()[0]
    def tag(link_id, name):
        db.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)",(name,))
        tid=db.execute("SELECT id FROM tags WHERE name=?",(name,)).fetchone()[0]
        db.execute("INSERT OR IGNORE INTO link_tags(link_id,tag_id) VALUES(?,?)",(link_id,tid))
    def put(url,title,folder,browser,fav,prot,added,src,tags):
        stats["seen"]+=1; n=norm_url(url)
        if not n: stats["skipped_invalid"]+=1; return
        if not browser: browser=",".join(sorted(bmap.get(n,[]))) or None
        fid=folder_id(folder,prot)
        row=db.execute("SELECT id,favorite,protected,folder_id,source_browser FROM links WHERE url_norm=?",(n,)).fetchone()
        if row:
            stats["dup_merged"]+=1; lid=row[0]
            db.execute("UPDATE links SET favorite=MAX(favorite,?),protected=MAX(protected,?),folder_id=CASE WHEN ?=1 THEN ? ELSE COALESCE(folder_id,?) END,source_browser=COALESCE(source_browser,?) WHERE id=?",(fav,prot,prot,fid,fid,browser,lid))
        else:
            cur=db.execute("INSERT INTO links(url,url_norm,title,folder_id,source_browser,favorite,protected,archived,added_at,status,source) VALUES(?,?,?,?,?,?,?,0,?, 'unchecked',?)",(url,n,title or url,fid,browser,fav,prot,added or now,src))
            lid=cur.lastrowid; stats["inserted"]+=1
        for t in tags: tag(lid,t)
    if a.bookmarks and Path(a.bookmarks).exists():
        src=sqlite3.connect("file:%s?mode=ro&immutable=1"%Path(a.bookmarks).resolve(),uri=True)
        for url,title,lf,folder,browser,first in src.execute("SELECT url,COALESCE(logical_title,title),logical_folder,folder,browser,first_seen FROM bookmarks WHERE COALESCE(status,'active')!='deleted'"):
            stats["from_bookmarks_db"]+=1; put(url,title,lf or folder,browser,0,0,first,"bookmarks_main.db",[])
        src.close()
    if a.netscape and Path(a.netscape).exists():
        p=Netscape(); p.feed(Path(a.netscape).read_text(encoding="utf-8",errors="replace"))
        for href,title,stack,add in p.items:
            stats["from_netscape"]+=1
            prot=1 if (stack and "Protected" in stack[-1]) else 0  # direct children of the Protected folder only
            folder=stack[-1] if stack else None
            added=time.strftime("%Y-%m-%dT%H:%M:%S%z",time.localtime(int(add))) if add and add.isdigit() else None
            tags=["protected"] if prot else (["favorites-cleaned"] if any("Favorites" in s for s in stack) else [])
            put(href,title,folder,None,1 if (prot or tags) else 0,prot,added,"netscape:"+Path(a.netscape).name,tags)
    db.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('seeded_at',?),('seed_stats',?)",(now,json.dumps(stats)))
    db.commit(); db.close(); os.chmod(out,0o600)
    print(json.dumps(stats))

if __name__=="__main__": main()

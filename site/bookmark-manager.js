/* Bookmark Manager (2026-09-26). Talks only to same-origin /api/links* on the hub (sign-in required). */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var PAGE = 200, offset = 0, total = 0, timer = null;
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
  function safeHref(u) { return /^(https?:|file:|mailto:|ftp:)/i.test(u || "") ? u : "#"; }
  function msg(t) { $("msg").textContent = t || ""; }
  function params() {
    var p = new URLSearchParams();
    if ($("q").value.trim()) p.set("q", $("q").value.trim());
    if ($("folder").value) p.set("folder", $("folder").value);
    if ($("tag").value) p.set("tag", $("tag").value);
    if ($("fav").checked) p.set("favorite", "1");
    if ($("arch").checked) p.set("archived", "1");
    p.set("limit", PAGE); p.set("offset", offset);
    return p.toString();
  }
  function post(path, body) {
    return fetch(path, { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { if (r.status === 401) { location.href = "/login?next=/site/bookmark-manager.html"; throw new Error("login"); } return r.json(); });
  }
  function fillSelect(sel, vals, keep) {
    var cur = sel.value, first = sel.options[0].outerHTML;
    sel.innerHTML = first + vals.map(function (v) { return '<option value="' + esc(v.value) + '">' + esc(v.label) + "</option>"; }).join("");
    if (keep) sel.value = cur;
  }
  function load(append) {
    if (!append) offset = 0;
    fetch("/api/links?" + params(), { credentials: "same-origin", cache: "no-store", headers: { "Accept": "application/json" } })
      .then(function (r) { if (r.status === 401) { location.href = "/login?next=/site/bookmark-manager.html"; throw new Error("login"); } return r.json(); })
      .then(function (d) {
        if (!d.ok) { msg(d.error || "Could not load links"); return; }
        total = d.total;
        var c = d.counts || {};
        $("counts").innerHTML = ["active", "favorite", "protected", "archived"].map(function (k) { return "<div><b>" + (c[k] || 0) + "</b>" + k + "</div>"; }).join("");
        fillSelect($("folder"), d.folders.map(function (f) { return { value: f.name, label: f.name + " (" + f.n + ")" }; }), true);
        fillSelect($("tag"), d.tags.map(function (t) { return { value: t, label: t }; }), true);
        $("folderList").innerHTML = d.folders.map(function (f) { return '<option value="' + esc(f.name) + '">'; }).join("");
        var html = d.items.map(function (it) {
          var tags = (it.tags || []).map(function (t) { return '<span class="tagp">' + esc(t) + "</span>"; }).join("");
          var acts = '<button data-a="edit" data-id="' + it.id + '">Edit</button>' +
            (it.archived ? '<button data-a="restore" data-id="' + it.id + '">Restore</button>'
              : (it.protected ? '<span class="lock">PROTECTED</span>' : '<button data-a="archive" data-id="' + it.id + '">Archive</button>'));
          return '<tr data-row="' + esc(JSON.stringify({ id: it.id, url: it.url, title: it.title, folder: it.folder || "", tags: it.tags || [] })) + '">' +
            '<td><button class="star' + (it.favorite ? " on" : "") + '" data-a="fav" data-id="' + it.id + '" title="Toggle favorite">★</button></td>' +
            '<td><a class="t" href="' + esc(safeHref(it.url)) + '" target="_blank" rel="noopener noreferrer">' + esc(it.title || it.url) + '</a><div class="u">' + esc(it.url) + "</div></td>" +
            '<td class="hide-s f">' + esc(it.folder || "") + "</td>" +
            '<td class="hide-s">' + tags + "</td>" +
            '<td class="hide-s f">' + esc(it.source_browser || "") + "</td>" +
            '<td class="act">' + acts + "</td></tr>";
        }).join("");
        if (append) $("rows").insertAdjacentHTML("beforeend", html); else $("rows").innerHTML = html || '<tr><td colspan="6" class="f">No links match.</td></tr>';
        var shown = Math.min(offset + d.items.length, total);
        $("shown").textContent = shown + " of " + total;
        $("moreBtn").hidden = shown >= total;
      })
      .catch(function (e) { if (e.message !== "login") msg("Hub not reachable. Open this page through the hub (https://pianomanuel.com:8444/site/)."); });
  }
  ["q"].forEach(function (id) { $(id).addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { load(false); }, 250); }); });
  ["folder", "tag", "fav", "arch"].forEach(function (id) { $(id).addEventListener("change", function () { load(false); }); });
  $("moreBtn").addEventListener("click", function () { offset += PAGE; load(true); });
  $("addBtn").addEventListener("click", function () { $("aId").value = ""; $("addf").reset(); $("aSave").textContent = "Save"; $("addf").classList.toggle("on"); $("aUrl").focus(); });
  $("addf").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var id = $("aId").value, body = { url: $("aUrl").value.trim(), title: $("aTitle").value.trim(), folder: $("aFolder").value.trim(), tags: $("aTags").value };
    if (id) body.id = +id;
    post(id ? "/api/links/edit" : "/api/links/add", body).then(function (r) {
      if (!r.ok) { msg(r.error === "duplicate" ? "Already in the database (id " + r.id + (r.archived ? ", archived" : "") + ")." : (r.error || "Save failed")); return; }
      msg(id ? "Saved." : "Added."); $("addf").classList.remove("on"); $("addf").reset(); $("aId").value = ""; load(false);
    });
  });
  $("rows").addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-a]"); if (!b) return;
    var id = +b.getAttribute("data-id"), a = b.getAttribute("data-a");
    if (a === "fav") return post("/api/links/favorite", { id: id }).then(function (r) { if (r.ok) b.classList.toggle("on", r.favorite); else msg(r.error); });
    if (a === "archive") { if (!confirm("Archive this link? (It is kept and can be restored.)")) return; return post("/api/links/archive", { id: id }).then(function (r) { msg(r.ok ? "Archived." : r.error); load(false); }); }
    if (a === "restore") return post("/api/links/restore", { id: id }).then(function (r) { msg(r.ok ? "Restored." : r.error); load(false); });
    if (a === "edit") {
      var row = JSON.parse(b.closest("tr").getAttribute("data-row"));
      $("aId").value = row.id; $("aUrl").value = row.url; $("aTitle").value = row.title || ""; $("aFolder").value = row.folder; $("aTags").value = row.tags.join(", ");
      $("aSave").textContent = "Save changes"; $("addf").classList.add("on"); window.scrollTo({ top: 0, behavior: "smooth" });
    }
  });
  load(false);
})();

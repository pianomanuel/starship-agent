/* Pianomanuel service worker. Cache the app shell only. Do not cache Mental Canvas. */
const VER = "pmano-2026-09-14-week";
const SHELL = ["./app.html","./ios.html","./index.html","./shop.html","./town.html","./board.html","./bookmarks.html","./manifest.json"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(VER).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VER).map(k => caches.delete(k)))));
});
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (u.hostname.includes("mentalcanvas")) return;
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request)));
});

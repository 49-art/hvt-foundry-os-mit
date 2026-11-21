/* Offline support: keeps the shop's page, words and pictures so it opens without signal. */
const VERSION = "0";
const EXTRA = [];
const CORE = ["./", "index.html", "style.css", "app.js", "i18n.js", "content.json", "manifest.webmanifest", "img/pattern.svg", "icons/icon-192.png", "icons/icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open("shop-" + VERSION).then(c => c.addAll(CORE.concat(EXTRA))).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== "shop-" + VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin || u.pathname.startsWith("/api/") || u.pathname.startsWith("/admin")) return;
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open("shop-" + VERSION).then(c => c.put(e.request, copy)); return r; })
    .catch(() => caches.match(e.request).then(m => m || caches.match("index.html"))));
});

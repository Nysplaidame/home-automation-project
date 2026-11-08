const CACHE = 'recomp-tracker-shell-v35';
const OCR_CACHE = 'recomp-ocr-6.0.1-6.1.2-fast-v1';
const SHELL = ['/', '/static/app-v2.js', '/static/nutrition-ocr.js', '/static/exercise-catalog.json', '/static/manifest.webmanifest'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
  self.skipWaiting();
});
self.addEventListener('activate', event => event.waitUntil(Promise.all([
  caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('recomp-tracker-shell-') && key !== CACHE || key.startsWith('recomp-ocr-') && key !== OCR_CACHE).map(key => caches.delete(key)))),
  self.clients.claim()
])));
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.pathname.startsWith('/api/') || url.pathname === '/healthz') return;
  if (url.origin === self.location.origin && url.pathname.startsWith('/static/ocr/')) {
    event.respondWith(caches.open(OCR_CACHE).then(async cache => {
      const cached = await cache.match(event.request);
      if (cached) return cached;
      const response = await fetch(event.request);
      if (response.ok) await cache.put(event.request, response.clone());
      return response;
    }));
    return;
  }
  event.respondWith(fetch(event.request).then(response => {
    const copy = response.clone();
    caches.open(CACHE).then(cache => cache.put(event.request, copy));
    return response;
  }).catch(() => caches.match(event.request)));
});

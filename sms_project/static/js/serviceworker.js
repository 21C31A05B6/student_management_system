/**
 * SMS (Student Management System) — PWA Service Worker
 * Handles offline caching, fast asset loading, and network resilience.
 */

const CACHE_NAME = 'sms-pwa-v1';
const STATIC_ASSETS = [
  '/',
  '/accounts/login/',
  '/static/manifest.json',
  '/static/css/sms.css',
  '/static/icons/icon-192.svg',
  '/static/icons/icon-512.svg',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js'
];

// Install Event: Cache Core App Shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[PWA] Pre-caching warning:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate Event: Clean up Old Caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event: Network-First with Cache Fallback for Pages, Cache-First for Static Assets
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests and Django API/Token requests
  if (request.method !== 'GET' || url.pathname.startsWith('/api/')) {
    return;
  }

  // Static Assets (CSS, JS, Fonts, Icons, CDN): Stale-While-Revalidate
  if (
    url.pathname.startsWith('/static/') ||
    url.hostname === 'cdn.jsdelivr.net' ||
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'font' ||
    request.destination === 'image'
  ) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const fetchPromise = fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      })
    );
    return;
  }

  // HTML Pages: Network-First with Cache Fallback
  if (request.headers.get('Accept') && request.headers.get('Accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return response;
        })
        .catch(async () => {
          const cachedResponse = await caches.match(request);
          if (cachedResponse) {
            return cachedResponse;
          }
          // Fallback to login or root if offline
          const fallback = await caches.match('/accounts/login/');
          return fallback || new Response(
            `<!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Offline - SMS</title>
              <style>
                body { background: #1e1b4b; color: #fff; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; padding: 20px; }
                .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); max-width: 400px; }
                h2 { color: #00cec9; margin-top: 0; }
                button { background: linear-gradient(135deg, #6c5ce7, #00cec9); border: none; padding: 10px 20px; color: white; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 15px; }
              </style>
            </head>
            <body>
              <div class="card">
                <h2>You're Offline</h2>
                <p>Please check your internet connection to continue using SMS (Student Management System).</p>
                <button onclick="window.location.reload()">Retry Connection</button>
              </div>
            </body>
            </html>`,
            { headers: { 'Content-Type': 'text/html' } }
          );
        })
    );
  }
});
